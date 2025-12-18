from a2a.types import AgentSkill

from a2a_acl.protocol.acl_message import Illocution
from a2a_acl.interface.interface import SkillDeclaration


def generate_param_example(i: int) -> str:
    if i is None:
        return ""
    else:
        return "(" + ("0," * i).removesuffix(",") + ")"


def pretty_print_example(s: SkillDeclaration):
    a = s.arity
    ex_param = "" if a == 0 else generate_param_example(a)
    ex = s.functor + ex_param
    return "(" + str(s.declaration_kind) + "," + ex + ")"


def parse_example(s: str) -> tuple[str, str]:
    """
    Example of input: '(achieve,share_secret(0))'
    Input encoded by pretty_print_example above.
    """
    s2 = s.removeprefix("(").removesuffix(")")
    (a, b) = s2.split(",")
    f = b.split("(")[0]
    return a, f


def encode_arity(a: int) -> str:
    if a is None:
        return ""
    else:
        return "(needs " + str(a) + " parameter" + ("s" if a > 1 else "") + ")"


def decode_arity(s: str) -> int:
    """
    Example of input: 'send a secret (needs 1 parameter)'
    Inputs are encoded by encode_arity above.
    Return 1 in this example.
    """
    l = s.split(" ")
    s1 = l[-2]
    return int(s1)


def a2a_skill_of_bdi_skill(s: SkillDeclaration) -> AgentSkill:
    return AgentSkill(
        id=s.functor,
        name=s.functor + " (from ACL agent)",
        description=s.doc + " " + encode_arity(s.arity),
        tags=[s.functor],
        examples=[pretty_print_example(s)],
    )


def bdi_skill_of_a2a_skill(s: AgentSkill) -> SkillDeclaration:
    """
    Exemple of skill for a ACL agent :
    AgentSkill(
        description='send a secret (needs 1 parameter)',
        examples=['(achieve,share_secret(0))'],
        id='share_secret',
        input_modes=None,
        name='share_secret (from ACL agent)',
        output_modes=None,
        security=None,
        tags=['share_secret']
        )
    """
    (a, f) = parse_example(s.examples[0])
    return SkillDeclaration(
        declaration_kind=Illocution(a),
        functor=f,
        arity=decode_arity(s.description),
        doc=s.description,
    )
