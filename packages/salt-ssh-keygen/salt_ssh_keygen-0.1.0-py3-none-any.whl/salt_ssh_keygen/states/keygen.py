__salt__ = {}
__opts__ = {}


# ssh-keygen -t rsa -b 4096 -N '' -f {{path}}/{{repo.key}}
def generate(name, bits=4096, type="rsa", passphrase="", user=None):
    ret = {"name": name, "result": False, "comment": "Generate key", "changes": {}}
    if __salt__["file.file_exists"](name):
        ret["result"] = True
        ret["comment"] = "Key exists"
        return ret
    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = "Key would be created"
        return ret
    _ = __salt__["cmd.run"](
        f"ssh-keygen -t {type} -b {bits} -N '{passphrase}' -f {name}", runas=user
    )
    ret["result"] = True
    ret["comment"] = "Key created"
    return ret
