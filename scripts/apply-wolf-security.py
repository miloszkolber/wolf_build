"""Apply the reviewed control-authentication backport only to its exact source."""
import hashlib
from pathlib import Path
import subprocess
import sys

SOURCE = "db709cfd3f0f49dfd7d00495940119309692b535"
EXPECTED = {
    "src/moonlight-protocol/crypto/crypto/utils.hpp": "e4800e23fa84ba08728f260982fc09b39b9d5dfc67bccf29ba6f756b86981fff",
    "src/moonlight-protocol/crypto/src/aes.hpp": "a6c9806bc9d79b17f9801bf7ed83af57b88095ba8e3b076a0dd27b860feb6e9a",
    "src/moonlight-protocol/crypto/src/crypto.cpp": "f8a8ef40579d0928812b91cf8927d95b4d3311b7404756a1f61f557915f4f4a3",
    "src/moonlight-protocol/crypto/src/sign.hpp": "eaf85ed615a345d3c55f6d811090a1bfc228048154b3641b9b56804e823017d1",
    "src/moonlight-protocol/crypto/src/utils.cpp": "2d1e837da2765fc1be810a404158caa857c91f4c974ac140ff257edd5b980018",
    "src/moonlight-protocol/moonlight/control.hpp": "57334ee366dde72c35ac342d940a567bf9d24afa8ec478ccd3b3a8bec4e6e4e5",
    "src/moonlight-server/control/control.cpp": "b586375db9af463520a8456ad0a8711459618573bfc89e0a900aaca7b86aaa87",
    "src/moonlight-server/gst-plugin/audio.hpp": "9f401f95545258fece52b7da098736ee9cb6d9d267b4caaf1a7859f6005a6dd5",
    "src/moonlight-server/gst-plugin/gstrtpmoonlightpay_audio.cpp": "4f7278c329e150792bf3ac82f3e9101bdca58acd52bfc0f45aa78159505d70f6",
    "src/moonlight-server/gst-plugin/gstrtpmoonlightpay_audio.hpp": "6dec216a7cf4ff6dae4fda733c2d502b1933f85076791ba5adbc2561c2b1c0d4",
    "src/moonlight-server/gst-plugin/utils.hpp": "91d1f5e800da85a7163f127cf8bf44de1b510f81b856a78d3bf3305cda0a9f2a",
    "src/moonlight-server/rest/endpoints.hpp": "26f5043d54f72e3ca1f50eda56f10b4d15b1beb0f58a1fac0816d924fc145867",
    "tests/testControl.cpp": "df986b0b26d2fed8a23fea8aa2ea5722501158fe0851913b0a09f71266a6d2c8",
    "tests/testCrypto.cpp": "cce11d38705717bd0ccbb1b57d83d45f3d5aaf900f84e62b4771d24bb8176004",
    "tests/testGSTPlugin.cpp": "9cad24217afe24b3cec26a58aed2286107cd8cfd25aaac597c6fce083e33be1f",
    "tests/testMoonlight.cpp": "8e372fea2825ce7a1fc29d2595cd60c512545917b9cb9ad1cb4a6845bb154aca",
}


def apply(root, revision, patch, followup):
    if revision != SOURCE:
        raise ValueError("Wolf revision needs security backport review")
    for name, expected in EXPECTED.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Wolf security backport source mismatch: " + name)
    subprocess.run(["git", "apply", "--check", str(patch)], cwd=root, check=True)
    subprocess.run(["git", "apply", str(patch)], cwd=root, check=True)
    subprocess.run(["git", "apply", "--check", str(followup)], cwd=root, check=True)
    subprocess.run(["git", "apply", str(followup)], cwd=root, check=True)


if __name__ == "__main__":
    apply(Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]).resolve(), Path(sys.argv[4]).resolve())
