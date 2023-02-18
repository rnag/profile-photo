from __future__ import annotations

from json import load
from pathlib import Path

from dataclass_wizard.abstractions import W

from ..models import Params


def load_to_model(model_cls: type[W], data: W | dict | str | Path, param: Params | str) -> W:
    """Load `data` as an instance of a model class `model_cls`."""

    if isinstance(data, model_cls):
        return data

    if isinstance(data, dict):
        return model_cls.from_dict(data)

    if isinstance(data, Path):
        with open(data) as in_file:
            return model_cls.from_dict(load(in_file))

    if isinstance(data, str):
        return model_cls.from_json(data)

    raise ValueError(f'Invalid type ({type(data)}) for `{param}`') from None
