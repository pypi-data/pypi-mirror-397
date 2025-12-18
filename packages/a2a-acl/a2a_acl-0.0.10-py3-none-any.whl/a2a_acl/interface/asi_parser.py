from a2a_acl.interface.interface import (
    SkillDeclaration,
    ACLAgentCard,
)
from a2a_acl.protocol.acl_message import Illocution


class SyntaxError(Exception):
    def __init__(self, message: str, filename: str, line: str):
        self.message = message
        self.filename = filename
        self.line = line


def read_file(intf: str) -> ACLAgentCard:
    with open(intf, "r") as f:
        l = f.readline()
        assert l.startswith("name = ")
        name = l.removeprefix("name = ").removesuffix("\n")

        l = f.readline()
        assert l.startswith("doc = ")
        agent_doc = l.removeprefix("doc = ").removesuffix("\n")

        lines = []

        for l in f:

            if l == "\n":
                pass
            else:
                try:
                    [k, functor, arity, doc] = l.removesuffix("\n").split(" : ")
                    match k:
                        case "tell" | "ask" | "achieve":
                            lines.append(
                                SkillDeclaration(
                                    declaration_kind=Illocution(k),
                                    doc=doc,
                                    functor=functor,
                                    arity=int(arity) if arity.isdigit() else None,
                                )
                            )
                        case "propose":
                            """proposal is an added illocution, with arity 1 (arity from file is ignored and can be a *)"""
                            lines.append(
                                SkillDeclaration(
                                    declaration_kind=Illocution(k),
                                    doc=doc,
                                    functor=functor,
                                    arity=1,
                                )
                            )
                        case _:
                            raise SyntaxError(intf, l, "Bad illocution: " + k)
                except SyntaxError as e:
                    raise e
                except Exception:
                    raise SyntaxError(intf, l, "bad line structure")

        return ACLAgentCard(name, agent_doc, lines, [])
