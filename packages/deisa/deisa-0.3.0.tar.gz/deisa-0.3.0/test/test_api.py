# =============================================================================
# Copyright (C) 2025 Commissariat a l'energie atomique et aux energies alternatives (CEA)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the names of CEA, nor the names of the contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written  permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# =============================================================================
import importlib

import pytest
from deisa.core import IDeisa, IBridge

from common import dask_env, ray_env

module_name = {
    dask_env.__name__: "deisa.dask",
    ray_env.__name__: "deisa.dask",  # TODO change to deisa.ray
}


@pytest.mark.parametrize("env_setup", [dask_env.__name__, ray_env.__name__])
def test_deisa_api(request, env_setup):
    client, cluster = request.getfixturevalue(env_setup)
    module = importlib.import_module(module_name[env_setup])
    deisa: IDeisa = module.Deisa(get_connection_info=lambda: client, wait_for_go=False)

    assert hasattr(deisa, 'close') and callable(deisa.close)
    assert hasattr(deisa, 'get_array') and callable(deisa.get_array)
    assert hasattr(deisa, 'register_sliding_window_callback') and callable(deisa.register_sliding_window_callback)
    assert hasattr(deisa, 'unregister_sliding_window_callback') and callable(deisa.unregister_sliding_window_callback)
    assert hasattr(deisa, "set") and callable(deisa.set)
    assert hasattr(deisa, "delete") and callable(deisa.delete)


@pytest.mark.parametrize("env_setup", [dask_env.__name__, ray_env.__name__])
def test_bridge_api(request, env_setup):
    client, cluster = request.getfixturevalue(env_setup)
    module = importlib.import_module(module_name[env_setup])
    bridge: IBridge = module.Bridge(id=0,
                                    arrays_metadata={},
                                    system_metadata={'connection': client, 'nb_bridges': 1},
                                    wait_for_go=False)

    assert hasattr(bridge, 'send') and callable(bridge.send)
    assert hasattr(bridge, 'get') and callable(bridge.get)
