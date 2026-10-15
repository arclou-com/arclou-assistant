"""Sincroniza o backlog do doc 05 com o GitHub (issues + Project).

Rode com: python3 scripts/github_backlog.py --sprint N [--dry-run]
Cria só a sprint N (as issues nascem no planejamento de cada sprint, não todas de uma vez).
O corpo de cada issue vem de docs/sprints/sprint-NN.md (seção "### <ID> · …"), com contexto,
escopo, critérios de aceite e testes. --update reescreve o corpo das issues que já existem.
Precisa do `gh` logado com os escopos `repo` e `project`.

Idempotente: issues já existentes (pelo ID no título, ex. "S2-07 ·") não são recriadas,
mas os campos do Project (Sprint, Pontos, Área, Status) são reaplicados.
"""
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
import time

OWNER = "arclou-com"
REPO = "arclou-assistant"
PROJECT_TITLE = "Arclou Assistant"
BACKLOG = pathlib.Path(__file__).resolve().parent.parent / "docs" / "05-backlog-sprints.md"
FIRST_SPRINT = dt.date(2026, 10, 19)
SPRINT_DAYS = 14
DRY = "--dry-run" in sys.argv
UPDATE = "--update" in sys.argv
SPECS = BACKLOG.parent / "sprints"
REPO_URL = f"https://github.com/{OWNER}/{REPO}/blob/develop"
if "--sprint" not in sys.argv:
    sys.exit("uso: python3 scripts/github_backlog.py --sprint N [--dry-run]")
SPRINT = int(sys.argv[sys.argv.index("--sprint") + 1])

AREAS = {
    "infra": ("5319e7", "Terraform e GCP"),
    "devops": ("0e8a16", "CI/CD, repositório e VM"),
    "backend": ("1d76db", "API, domínio e adapters"),
    "agent": ("d93f0b", "LangGraph, prompts e evals"),
    "frontend": ("fbca04", "Next.js e telas"),
    "docs": ("c5def5", "Documentação e processos"),
}
EXTRA_LABELS = {
    "epic": ("3e4b9e", "Objetivo da sprint (as tasks são sub-issues)"),
    "track:front": ("f9d0c4", "Trilha de front contra o mock"),
}
STATUS = ["Backlog", "Todo", "In Progress", "In Review", "Done"]
STATUS_COLORS = {"Backlog": "GRAY", "Todo": "BLUE", "In Progress": "YELLOW", "In Review": "PURPLE", "Done": "GREEN"}


def gh(*args: str, input_: str | None = None) -> str:
    for attempt in range(5):
        r = subprocess.run(["gh", *args], capture_output=True, text=True, input=input_)
        if r.returncode == 0:
            return r.stdout
        err = r.stderr.lower()
        if any(k in err for k in ("rate limit", "abuse", "something went wrong", "502", "504", "timeout")):
            time.sleep(30 * (attempt + 1))
            continue
        raise RuntimeError(f"gh {' '.join(args[:3])}…: {r.stderr.strip()}")
    raise RuntimeError("rate limit persistente")


def gql(query: str, **variables) -> dict:
    payload = json.dumps({"query": query, "variables": variables})
    return json.loads(gh("api", "graphql", "--input", "-", input_=payload))["data"]


def clean(text: str) -> str:
    return re.sub(r"\*\*|`", "", text).strip()


def short_title(text: str, limit: int = 90) -> str:
    text = clean(text)
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",;:(")
    return cut + "…"


def parse_backlog() -> list[dict]:
    sprints = []
    current = None
    for line in BACKLOG.read_text().splitlines():
        m = re.match(r"## Sprint (\d+) — (.+?) \((.+)\)$", line)
        if m:
            current = {"n": int(m[1]), "theme": m[2], "dates": m[3], "objective": "", "tasks": []}
            sprints.append(current)
            continue
        if line.startswith("## "):
            current = None
            continue
        if current is None:
            continue
        if line.startswith("**Objetivo:**"):
            current["objective"] = clean(line.removeprefix("**Objetivo:**"))
        if line.startswith("| S"):
            c = [x.strip() for x in line.strip("|").split("|")]
            current["tasks"].append({
                "id": c[0], "task": c[1], "area": c[2],
                "points": int(c[3]) if c[3].isdigit() else None, "acceptance": c[4],
            })
    return sprints


def ensure_labels() -> None:
    existing = {l["name"] for l in json.loads(gh("label", "list", "-R", f"{OWNER}/{REPO}", "--limit", "200", "--json", "name"))}
    wanted = {f"area:{k}": v for k, v in AREAS.items()} | EXTRA_LABELS
    for name, (color, desc) in wanted.items():
        if name not in existing and not DRY:
            gh("label", "create", name, "-R", f"{OWNER}/{REPO}", "--color", color, "--description", desc)


def ensure_project() -> dict:
    org = gql("""query($o:String!){organization(login:$o){id projectsV2(first:50){nodes{id number title}}}}""", o=OWNER)["organization"]
    proj = next((p for p in org["projectsV2"]["nodes"] if p["title"] == PROJECT_TITLE), None)
    if not proj:
        proj = gql("""mutation($o:ID!,$t:String!){createProjectV2(input:{ownerId:$o,title:$t}){projectV2{id number title}}}""",
                   o=org["id"], t=PROJECT_TITLE)["createProjectV2"]["projectV2"]
        repo_id = gql("""query($o:String!,$r:String!){repository(owner:$o,name:$r){id}}""", o=OWNER, r=REPO)["repository"]["id"]
        gql("""mutation($p:ID!,$r:ID!){linkProjectV2ToRepository(input:{projectId:$p,repositoryId:$r}){repository{id}}}""", p=proj["id"], r=repo_id)
    return proj


def get_fields(project_id: str) -> dict:
    q = """query($p:ID!){node(id:$p){... on ProjectV2{fields(first:50){nodes{
      ... on ProjectV2Field{id name dataType}
      ... on ProjectV2SingleSelectField{id name dataType options{id name}}
      ... on ProjectV2IterationField{id name dataType configuration{iterations{id title startDate} completedIterations{id title startDate}}}}}}}}"""
    return {f["name"]: f for f in gql(q, p=project_id)["node"]["fields"]["nodes"] if f}


def ensure_fields(project_id: str, n_sprints: int) -> dict:
    fields = get_fields(project_id)
    status = fields["Status"]
    if [o["name"] for o in status["options"]] != STATUS:
        opts = [{"name": s, "color": STATUS_COLORS[s], "description": ""} for s in STATUS]
        gql("""mutation($f:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]){updateProjectV2Field(input:{fieldId:$f,singleSelectOptions:$o}){projectV2Field{... on ProjectV2SingleSelectField{id}}}}""",
            f=status["id"], o=opts)
    if "Sprint" not in fields:
        its = [{"title": f"Sprint {i}", "startDate": (FIRST_SPRINT + dt.timedelta(days=SPRINT_DAYS * i)).isoformat(),
                "duration": SPRINT_DAYS} for i in range(n_sprints)]
        gql("""mutation($p:ID!,$c:ProjectV2IterationFieldConfigurationInput!){createProjectV2Field(input:{projectId:$p,dataType:ITERATION,name:"Sprint",iterationConfiguration:$c}){projectV2Field{... on ProjectV2IterationField{id}}}}""",
            p=project_id, c={"startDate": FIRST_SPRINT.isoformat(), "duration": SPRINT_DAYS, "iterations": its})
    if "Pontos" not in fields:
        gql("""mutation($p:ID!){createProjectV2Field(input:{projectId:$p,dataType:NUMBER,name:"Pontos"}){projectV2Field{... on ProjectV2Field{id}}}}""", p=project_id)
    for name, values in {"Área": list(AREAS), "Prioridade": ["P0", "P1", "P2"]}.items():
        if name not in fields:
            opts = [{"name": v, "color": "GRAY", "description": ""} for v in values]
            gql("""mutation($p:ID!,$n:String!,$o:[ProjectV2SingleSelectFieldOptionInput!]){createProjectV2Field(input:{projectId:$p,dataType:SINGLE_SELECT,name:$n,singleSelectOptions:$o}){projectV2Field{... on ProjectV2SingleSelectField{id}}}}""",
                p=project_id, n=name, o=opts)
    return get_fields(project_id)


def existing_issues() -> dict:
    out = gh("issue", "list", "-R", f"{OWNER}/{REPO}", "--state", "all", "--limit", "1000", "--json", "number,title,id")
    issues = {}
    for i in json.loads(out):
        key = i["title"].split(" · ")[0]
        issues[key] = i
    return issues


def create_issue(title: str, body: str, labels: list[str]) -> dict:
    args = ["api", f"repos/{OWNER}/{REPO}/issues", "-f", f"title={title}", "-f", f"body={body}"]
    for l in labels:
        args += ["-f", f"labels[]={l}"]
    data = json.loads(gh(*args))
    time.sleep(1.2)  # limite secundário de criação de conteúdo
    return {"number": data["number"], "id": data["node_id"], "db_id": data["id"], "title": title}


def load_specs(n: int) -> dict:
    """Seções '### <ID> · título' do arquivo de especificação da sprint."""
    path = SPECS / f"sprint-{n:02d}.md"
    if not path.exists():
        return {}
    specs, current = {}, None
    for line in path.read_text().splitlines():
        m = re.match(r"### (S\d+-F?\d+) · ", line)
        if m:
            current = m[1]
            specs[current] = []
        elif line.strip() == "---" or line.startswith("## "):
            current = None
        elif current:
            specs[current].append(line)
    return {k: "\n".join(v).strip() for k, v in specs.items()}


def task_body(sprint: dict, t: dict, spec: str | None) -> str:
    pts = t["points"] if t["points"] is not None else "—"
    track = "Trilha de front (contra o mock do contrato)" if "-F" in t["id"] else "Trilha back/infra"
    header = (f"> **Sprint {sprint['n']}** ({sprint['dates']}) · **Área:** {t['area']} · **Pontos:** {pts} · {track}\n"
              f"> Especificação: [`docs/sprints/sprint-{sprint['n']:02d}.md`]({REPO_URL}/docs/sprints/sprint-{sprint['n']:02d}.md)\n\n")
    dod = (f"\n\n### Definition of Done\n- [ ] PR para `develop` revisado, CI verde\n- [ ] Testes escritos e passando\n"
           f"- [ ] Deploy em staging com smoke verde\n- [ ] Documentação atualizada\n\n"
           f"Detalhes em [docs/05]({REPO_URL}/docs/05-backlog-sprints.md#definition-of-done-vale-para-toda-task).\n")
    if spec:
        return header + spec + dod
    return (header + f"{clean(t['task'])}\n\n### Critérios de aceite\n- [ ] {clean(t['acceptance'])}" + dod)


def set_field(project_id: str, item_id: str, field_id: str, value: dict) -> None:
    gql("""mutation($p:ID!,$i:ID!,$f:ID!,$v:ProjectV2FieldValue!){updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i,fieldId:$f,value:$v}){projectV2Item{id}}}""",
        p=project_id, i=item_id, f=field_id, v=value)


def main() -> None:
    all_sprints = parse_backlog()
    sprints = [s for s in all_sprints if s["n"] == SPRINT]
    if not sprints:
        sys.exit(f"Sprint {SPRINT} não existe no doc 05")
    if DRY:
        for s in sprints:
            print(f"Sprint {s['n']} — {s['theme']}: {len(s['tasks'])} tasks")
            for t in s["tasks"]:
                print(f"  {t['id']} · {short_title(t['task'])} ({t['area']}, {t['points']})")
        return
    ensure_labels()
    proj = ensure_project()
    fields = ensure_fields(proj["id"], len(all_sprints))
    status_opt = {o["name"]: o["id"] for o in fields["Status"]["options"]}
    area_opt = {o["name"]: o["id"] for o in fields["Área"]["options"]}
    prio_opt = {o["name"]: o["id"] for o in fields["Prioridade"]["options"]}
    sprint_cfg = fields["Sprint"]["configuration"]
    iterations = {i["title"]: i["id"] for i in sprint_cfg["iterations"] + sprint_cfg["completedIterations"]}
    issues = existing_issues()

    for s in sprints:
        epic_key = f"Sprint {s['n']}"
        epic = issues.get(epic_key)
        if not epic:
            pts = sum(t["points"] or 0 for t in s["tasks"])
            body = f"**{s['dates']}** · {pts} pontos\n\n**Objetivo:** {s['objective'] or s['theme']}\n\nAs tasks da sprint são sub-issues desta issue.\n"
            epic = create_issue(f"{epic_key} · {s['theme']}", body, ["epic"])
            issues[epic_key] = epic
        epic_num = epic["number"]
        specs = load_specs(s["n"])
        missing = [t["id"] for t in s["tasks"] if t["id"] not in specs]
        if missing:
            print(f"  aviso: sem especificação detalhada para {', '.join(missing)}")
        for t in s["tasks"]:
            iss = issues.get(t["id"])
            created = False
            if not iss:
                labels = [f"area:{t['area']}"] + (["track:front"] if "-F" in t["id"] else [])
                iss = create_issue(f"{t['id']} · {short_title(t['task'])}", task_body(s, t, specs.get(t["id"])), labels)
                issues[t["id"]] = iss
                created = True
            elif UPDATE:
                gh("issue", "edit", str(iss["number"]), "-R", f"{OWNER}/{REPO}", "--body-file", "-",
                   input_=task_body(s, t, specs.get(t["id"])))
            if created:
                db_id = iss.get("db_id") or json.loads(gh("api", f"repos/{OWNER}/{REPO}/issues/{iss['number']}"))["id"]
                gh("api", "-X", "POST", f"repos/{OWNER}/{REPO}/issues/{epic_num}/sub_issues", "-F", f"sub_issue_id={db_id}")
            item = gql("""mutation($p:ID!,$c:ID!){addProjectV2ItemById(input:{projectId:$p,contentId:$c}){item{id}}}""",
                       p=proj["id"], c=iss["id"])["addProjectV2ItemById"]["item"]["id"]
            set_field(proj["id"], item, fields["Sprint"]["id"], {"iterationId": iterations[epic_key]})
            set_field(proj["id"], item, fields["Status"]["id"], {"singleSelectOptionId": status_opt["Todo" if s["n"] == 0 else "Backlog"]})
            set_field(proj["id"], item, fields["Área"]["id"], {"singleSelectOptionId": area_opt[t["area"]]})
            set_field(proj["id"], item, fields["Prioridade"]["id"], {"singleSelectOptionId": prio_opt["P0" if s["n"] <= 1 else "P1"]})
            if t["points"] is not None:
                set_field(proj["id"], item, fields["Pontos"]["id"], {"number": t["points"]})
            print(f"  #{iss['number']} {t['id']}{' (nova)' if created else ''}")
        item = gql("""mutation($p:ID!,$c:ID!){addProjectV2ItemById(input:{projectId:$p,contentId:$c}){item{id}}}""",
                   p=proj["id"], c=epic["id"])["addProjectV2ItemById"]["item"]["id"]
        set_field(proj["id"], item, fields["Sprint"]["id"], {"iterationId": iterations[epic_key]})
        print(f"Sprint {s['n']} ok (épico #{epic_num})")
    print(f"Project: https://github.com/orgs/{OWNER}/projects/{proj['number']}")


if __name__ == "__main__":
    main()
