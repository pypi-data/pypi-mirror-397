#
#   Imandra Inc.
#
#   imx.py
#

import asyncio
import sys
from typing import Literal, TypedDict, assert_never

import typer
from imandrax_api_models import DecomposeRes, InstanceRes, VerifyRes
from imandrax_api_models.client import (
    ImandraXAsyncClient,
    get_imandrax_async_client,
    get_imandrax_client,
)
from imandrax_api_models.context_utils import (
    format_decomp_res,
    format_eval_res,
    #format_vg_res,
)
from iml_query.processing import (
    extract_decomp_reqs,
    extract_instance_reqs,
    extract_verify_reqs,
)
from iml_query.processing.decomp import DecompReqArgs
from iml_query.tree_sitter_utils import get_parser

from enum import StrEnum
class IMX_Status(StrEnum):
    """
    """
    UNKNOWN = 'Unkown'
    ADMITTED = 'Admitted'
    ERROR = 'Error'


def check_model(model : str) -> bool:
    """ 
    Check that the model is admitted to ImandraX
    """
    c = get_imandrax_client()
    eval_res = c.eval_model(src=model, with_vgs=False, with_decomps=False)

    return format_eval_res(eval_res)

def run_eval(model : str, eval_str : str) -> str:
    """
    Run evaluation
    """

    c = get_imandrax_client()
    eval_res = c.eval_src(model)

    return ""


class VGItem(TypedDict):
    kind: Literal["verify", "instance"]
    src: str
    start_point: tuple[int, int]
    end_point: tuple[int, int]

def _collect_vgs(iml: str) -> list[VGItem]:
    tree = get_parser().parse(iml.encode("utf-8"))
    iml, tree, verify_reqs, verify_req_ranges = extract_verify_reqs(iml, tree)
    iml, tree, instance_reqs, instance_req_ranges = extract_instance_reqs(iml, tree)

    # Collect
    vg_items: list[VGItem] = []
    for req, req_range in zip(verify_reqs, verify_req_ranges, strict=True):
        vg_items.append(
            {
                "kind": "verify",
                "src": req["src"],
                "start_point": (req_range.start_point[0], req_range.start_point[1]),
                "end_point": (req_range.end_point[0], req_range.end_point[1]),
            }
        )
    for req, req_range in zip(instance_reqs, instance_req_ranges, strict=False):
        vg_items.append(
            {
                "kind": "instance",
                "src": req["src"],
                "start_point": (req_range.start_point[0], req_range.start_point[1]),
                "end_point": (req_range.end_point[0], req_range.end_point[1]),
            }
        )
    vg_items.sort(key=lambda x: x["start_point"])
    return vg_items

def check_instance (model : str, instance_query : str) -> bool:
    """
    Run the instance request and return True/False if the instance is Sat
    """
    async def _async_check_vg() -> list[VerifyRes | InstanceRes]:
        iml = model + "\n" + instance_query
        vgs = _collect_vgs(iml)

        vg_with_idx: list[tuple[int, VGItem]] = [
            (i, vg) for (i, vg) in enumerate(vgs, 1)
        ]

        async def _check_vg(
            vg: VGItem,
            i: int,
            c: ImandraXAsyncClient,
        ) -> VerifyRes | InstanceRes:
            match vg["kind"]:
                case "verify":
                    res = await c.verify_src(src=vg["src"])
                case "instance":
                    res = await c.instance_src(src=vg["src"])
                case _:
                    assert_never(vg["kind"])
            #print(f"{i}: {vg['kind']} ({vg['src']})")
            #print(format_vg_res(res))
            return res

        async with get_imandrax_async_client() as c:
            eval_res = await c.eval_model(src=iml)
            #print(format_eval_res(eval_res, iml))
            if eval_res.has_errors:
                print("Error(s) found in IML file. Exiting.")
                sys.exit(1)
                return
            #print("\n" + "=" * 5 + "VG" + "=" * 5 + "\n")
            tasks = [_check_vg(vg, i, c) for (i, vg) in vg_with_idx]
            return await asyncio.gather(*tasks)

    vg_res_list = asyncio.run(_async_check_vg())

    if len(vg_res_list) == 0:
        raise Exception(f"Failed to get response")

    return vg_res_list[0].res_type == 'sat'

class DecompItem(TypedDict):
    req_args: DecompReqArgs
    start_point: tuple[int, int]
    end_point: tuple[int, int]

def _collect_decomps(iml: str) -> list[DecompItem]:
    tree = get_parser().parse(iml.encode("utf-8"))
    iml, tree, decomp_reqs, ranges = extract_decomp_reqs(iml, tree)

    decomp_items: list[DecompItem] = [
        DecompItem(
            req_args=req,
            start_point=range_.start_point,
            end_point=range_.end_point,
        )
        for req, range_ in zip(decomp_reqs, ranges, strict=True)
    ]

    decomp_items.sort(key=lambda x: x["start_point"])
    return decomp_items

def run_decomp(model : str, decomp_request : str):
    """
    Run the decomp request
    """
    async def _async_check_decomp() -> list[DecomposeRes]:
        iml = model + "\n" + decomp_request
        decomps = _collect_decomps(iml)

        decomp_with_idx: list[tuple[int, DecompItem]] = [
            (i, decomp) for (i, decomp) in enumerate(decomps, 1)
        ]

        async def _check_decomp(
            decomp: DecompItem, i: int, c: ImandraXAsyncClient
        ) -> DecomposeRes:
            #print(f"{i}: decompose {decomp['req_args']['name']}")
            res = await c.decompose(**decomp["req_args"])
            #print(format_decomp_res(res))
            return res

        async with get_imandrax_async_client() as c:
            eval_res = await c.eval_model(src=iml)
            #print(format_eval_res(eval_res, iml))
            if eval_res.has_errors:
                typer.echo("Error(s) found in IML file. Exiting.")
                sys.exit(1)
                return

            #print("\n" + "=" * 5 + "Decomp" + "=" * 5 + "\n")
            tasks = [_check_decomp(decomp, i, c) for (i, decomp) in decomp_with_idx]
            return await asyncio.gather(*tasks)

    decomp_res_list = asyncio.run(_async_check_decomp())

    return decomp_res_list[0]