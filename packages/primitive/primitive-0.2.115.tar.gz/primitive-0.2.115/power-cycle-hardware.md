# Power Cycling Machines

### Prerequisites

If you have not setup the CLI you may need it for some options:

```bash
cd ~/Development/primitivecorp/
git clone git@github.com:primitivecorp/primitive-cli.git
cd primitive-cli
uv .venv
source .venv/bin/activate
uv pip install -e .
primitive --host api.dev.primitive.tech config
> You can find or create a Primitive API token at https://app.dev.primitive.tech/account/tokens
> Please enter your Primitive API token:

# verify with
primitive --host api.dev.primitive.tech whoami
```

## 1: Power Cycling via the Primitive UI

Navigate to the Hardware table (https://app.dev.primitive.tech/primitive/hardware)
On the righthand side of the rows in the table you can find the '...' action's menu. Select Power Cycle.
You can also skip to the URL directly: https://app.dev.primitive.tech/primitive/hardware/freddie-murcery/power-cycle

A form with jobs will be presented.

- OOB Power Cycle will use the controller node to power cycle the machine
- Power Cycle will use the selected target node to power cycle the machine

## 2: Accessing the BMC's UI with the Primitive CLI

If you have access to a controller node such as `george-michael` from your local machine, you can use the Primitive CLI to handle tunneling to the correct connections to tunnel to the BMC's UI.

> Note: These commands can be obtained on the UI if you reserve your desired hardware. Navigate to the Hardware table (https://app.dev.primitive.tech/primitive/hardware), and click Reserve on your desired machine. In the "..." action menu on the table, you can now click the BMC button. This will copy the appropriate command to use in your CLI.

On the standard network run:

```bash
primitive --host api.dev.primitive.tech hardware bmc freddie-murcery
```

> Note: If you are running over tailscale or some other VPN, please use the `--hostname-override` flag to specifiy the first hop:

```bash
primitive --host api.dev.primitive.tech hardware bmc freddie-murcery --hostname-override george-michael
```

Running the command will provide the URLs to get the BMC credentials from the Primitive UI as well as the tunnel UI:

```bash
$ primitive --host api.dev.primitive.tech hardware bmc freddie-murcery
> Primitive CLI 0.2.113
>   ○ BMC Connection Details:    https://app.dev.primitive.tech/primitive/hardware/freddie-murcery?connectionType=BMC#connectionDetails
>   ○ BMC UI:                    https://127.0.0.1:8080
>   ○ Target Web TTY:            https://127.0.0.1:8080/cgi/url_redirect.cgi?url_name=man_ikvm_html5_bootstrap
> Connecting to 192.168.1.221:22 as linuxadmin...
> Listening on 127.0.0.1:8080 -> 192.168.10.102:443
```

After logging in to the BMC's UI, select the Power Button on the righthand side of the screen. This brings up the Power Control UI. Select the option you would like.

## 3: Power Cycling the Box via the Primitive Python Library

You can use the Primitive Python library to interface with Hardware via Redfish. This assumes you are on a machine that has network access ot the BMC you would like to access. For this example, assume you have access to george-michael such as:

```
ssh george-michael
sudo su
cd
source .venv/bin/activate
ipython
# ... now paste your script
```

The script:

```python
from primitive.client import Primitive
from primitive.network.redfish import RedfishClient

primitive = Primitive(host='api.dev.primitive.tech')

hardware = primitive.hardware.get_hardware_from_slug_or_id('freddie-murcery')
hardware_secret = primitive.hardware.get_hardware_secret(hardware_id=hardware["id"])

bmc_hostname = hardware.get("defaultBmcIpv4Address", None)
bmc_username = hardware_secret.get("bmcUsername", None)
bmc_password = hardware_secret.get("bmcPassword", "")

redfish = RedfishClient(
    host=bmc_hostname, username=bmc_username, password=bmc_password
)
redfish.compute_system_reset(system_id="1", reset_type="ForceRestart")
```

## 4: Power Cycling the Box via the BMC Directly

1. the hostname of the machine's BMC
2. the username and password of the BMC's admin account
3. access to the bmc
4. running reset on the SMASH prompt

### 1. to obtain the hostname of the machine's BMC:

The BMC hostname can be obtained from the Hardware Table under `BMC IPv4 Address`

### 2. to obtain the username and password of a machine:

if you go to the hardware's detail page, say for freddie at https://app.dev.primitive.tech/primitive/hardware/freddie-murcery
towards the bottom there is a Connection Details header. if you select BMC and click Show Details you'll be presented with the BMC's username and password. we'd like to keep these centralized and not in the slack if possible

### 3. access to the bmc

first access a host that is on the same network as the node's BMC, such as george-michael
access george-michael on the local network: `ssh linuxadmin@192.168.1.221`
access george-michael on the primitive tailscale network: `ssh linuxadmin@george-michael`

now access the BMC's SSH shell using the obtained values from the UI: `ssh <username>@<host>`

#### 4. running reset on the SMASH prompt

You need to move into the correct devices directory then run the reset command to power cycle the node the BMC has access to.

```bash
# your host
$ ssh linuxadmin@192.168.1.221
Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.8.0-88-generic x86_64)
# on george-michael
linuxadmin@george-michael:~$ ssh <username>@<ip address>
primitiveadmin@192.168.10.102's password:

Insyde SMASH-CLP System Management Shell, versions 1.05
Copyright (c) 2015-2016 by Insyde International CO., Ltd.
All Rights Reserved


-> cd /system1/pwrmgtsvc1
/system1/pwrmgtsvc1

-> reset
/system1/pwrmgtsvc1
reset done...
```
