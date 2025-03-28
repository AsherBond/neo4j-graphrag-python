#  Copyright (c) "Neo4j"
#  Neo4j Sweden AB [https://neo4j.com]
#  #
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  #
#      https://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

import neo4j
from neo4j import GraphDatabase
from neo4j_graphrag.indexes import create_vector_index, drop_index_if_exists

try:
    from qdrant_client import QdrantClient, models
except ImportError as e:
    missing_module = str(e).split("'")[1]
    if missing_module == "qdrant_client":
        raise ImportError(
            "The 'qdrant-client' package is missing. Please install it by running "
            '`poetry install --extras "qdrant"` or `pip install qdrant-client`, or follow the instructions '
            "in the Qdrant examples section of the README at https://github.com/neo4j/neo4j-graphrag-python/"
        ) from e
    else:
        raise

# biology
EMBEDDING_BIOLOGY = [
    -0.04312172904610634,
    0.027684900909662247,
    -0.03451697900891304,
    0.033050164580345154,
    -0.02548302337527275,
    -0.02422613650560379,
    0.06078026071190834,
    0.05728934705257416,
    0.026537826284766197,
    0.06596288084983826,
    -0.011962010525166988,
    -0.03995208814740181,
    -0.08753148466348648,
    0.048919592052698135,
    -0.12121172994375229,
    0.0046921405009925365,
    -0.11684603989124298,
    0.011236454360187054,
    -0.08468407392501831,
    0.00615630391985178,
    -0.01894194260239601,
    0.07591243833303452,
    0.010966621339321136,
    -0.0035629894118756056,
    -0.07222436368465424,
    -0.0038335833232849836,
    -0.013435023836791515,
    -0.01072753593325615,
    -0.019481584429740906,
    -0.08576139807701111,
    -0.005984509363770485,
    0.06511891633272171,
    0.047047052532434464,
    -0.008832206949591637,
    -0.02516607940196991,
    0.030757833272218704,
    0.01017201878130436,
    -0.035205237567424774,
    0.0754496157169342,
    0.049298327416181564,
    -0.008700424805283546,
    -0.042502958327531815,
    -0.007827227003872395,
    0.022037239745259285,
    0.01526452787220478,
    0.057564627379179,
    0.01117363478988409,
    -0.022880272939801216,
    0.002632720861583948,
    -0.06985171139240265,
    -0.04440313205122948,
    -0.02955677919089794,
    -0.12585243582725525,
    0.02834390103816986,
    0.047075871378183365,
    0.039754725992679596,
    -0.062267716974020004,
    -0.02022026665508747,
    -0.02561432123184204,
    -0.06196143478155136,
    0.06283645331859589,
    -0.010700947605073452,
    -0.009793519042432308,
    0.0676884651184082,
    0.07930963486433029,
    -0.05287032946944237,
    0.005661565810441971,
    0.04567752033472061,
    0.01226893998682499,
    0.0024454575031995773,
    0.03628166392445564,
    -0.01688201352953911,
    -0.0009241311927326024,
    0.10099577158689499,
    0.0851878672838211,
    -0.0056961155496537685,
    -0.012224642559885979,
    0.03202442824840546,
    0.07562054693698883,
    -0.030286865308880806,
    0.031771108508110046,
    -0.07060682028532028,
    -0.01805405505001545,
    0.03888492286205292,
    0.013361049816012383,
    -0.025815952569246292,
    0.06777660548686981,
    0.05500587448477745,
    -0.09657344222068787,
    0.06346127390861511,
    -0.03499232605099678,
    -0.06173454597592354,
    0.03703204542398453,
    -0.008920160122215748,
    -0.1170671284198761,
    0.05101491138339043,
    0.02324659377336502,
    -0.11062400788068771,
    0.05613391101360321,
    0.1953216791152954,
    -0.046223606914281845,
    0.0207725428044796,
    -0.037569694221019745,
    0.09747911989688873,
    0.03182050585746765,
    -0.09000813961029053,
    -0.03741106390953064,
    -0.001107109128497541,
    0.05828772485256195,
    0.03561848774552345,
    -0.012867141515016556,
    0.04318442568182945,
    -0.007168568670749664,
    0.10120371729135513,
    0.015526260249316692,
    0.046518243849277496,
    0.09026871621608734,
    -0.025434499606490135,
    0.07185306400060654,
    0.006204536650329828,
    -0.025380434468388557,
    -0.03805668652057648,
    -0.046537771821022034,
    -0.028066400438547134,
    -0.04620446264743805,
    -0.04175203666090965,
    -0.05594577267765999,
    -7.522815605061209e-33,
    0.0032660849392414093,
    -0.0987364873290062,
    0.048021912574768066,
    0.026744935661554337,
    -0.04386494308710098,
    0.033061958849430084,
    -0.0033691301941871643,
    -0.09897749125957489,
    -0.0019302349537611008,
    0.011837359517812729,
    -0.05590499937534332,
    -0.010936262086033821,
    0.0011399721261113882,
    0.043522097170352936,
    0.024741550907492638,
    0.030598435550928116,
    -0.10856965184211731,
    0.09524074196815491,
    -0.011383255943655968,
    0.0199135635048151,
    -0.055631425231695175,
    0.02365952730178833,
    -0.02242668904364109,
    -0.046286772936582565,
    0.0020421564113348722,
    -0.029465770348906517,
    -0.0544230192899704,
    -0.08019289374351501,
    0.055107232183218,
    -0.010339600965380669,
    0.016182616353034973,
    -0.019025344401597977,
    -0.06670568138360977,
    0.0005314883892424405,
    0.01192407961934805,
    -0.07481196522712708,
    0.04253043606877327,
    -0.05555248260498047,
    -0.007614267058670521,
    -0.012775871902704239,
    -0.0022697255481034517,
    -0.03448570892214775,
    0.036854878067970276,
    -0.04938317835330963,
    0.08296490460634232,
    0.03675423562526703,
    -0.003109127515926957,
    0.00267212837934494,
    -0.06396905332803726,
    0.019167274236679077,
    -0.020589588209986687,
    -0.017604926601052284,
    0.10695572197437286,
    -0.09441392868757248,
    0.021013183519244194,
    0.04480829834938049,
    -0.027837105095386505,
    -0.0011123925214633346,
    -0.08835164457559586,
    0.017125461250543594,
    0.06728456914424896,
    0.12567774951457977,
    -0.06033247709274292,
    0.03521595522761345,
    0.07578440755605698,
    -0.03819991648197174,
    -0.09275069832801819,
    -0.09814322739839554,
    0.021795116364955902,
    0.025850528851151466,
    -0.0532839410007,
    -0.054003648459911346,
    -0.026674047112464905,
    -0.10661919414997101,
    0.004801975563168526,
    0.016014324501156807,
    0.0004556076892185956,
    0.01613032817840576,
    -0.09400207549333572,
    0.012587584555149078,
    0.01425306685268879,
    -0.03173312172293663,
    -0.04417256638407707,
    -0.034732427448034286,
    -0.03740209341049194,
    0.07315755635499954,
    0.022384824231266975,
    -0.0658881664276123,
    5.2405772294150665e-05,
    0.019976867362856865,
    -0.054833319038152695,
    -0.04896378144621849,
    -0.013568416237831116,
    -0.011525219306349754,
    0.000531611789483577,
    3.594654745316847e-33,
    0.006438549142330885,
    -0.07441601902246475,
    -0.04541584476828575,
    0.04658213630318642,
    0.05004657804965973,
    0.06633730232715607,
    -0.009470561519265175,
    -0.020702792331576347,
    0.003479442559182644,
    0.017732439562678337,
    0.0058183688670396805,
    0.0337534099817276,
    0.06103092059493065,
    -0.010244826786220074,
    -0.049173060804605484,
    -0.039285846054553986,
    -0.019474590197205544,
    -0.005957481451332569,
    -0.007637818343937397,
    -0.001945863594301045,
    -0.10105801373720169,
    0.07999070733785629,
    -0.002908281981945038,
    -0.055638041347265244,
    -0.013490298762917519,
    0.07804659008979797,
    -0.017962178215384483,
    0.05879015102982521,
    -0.02929818443953991,
    0.010783063247799873,
    -0.017044004052877426,
    0.03597024083137512,
    -0.010958723723888397,
    -0.020666809752583504,
    0.030345136299729347,
    0.08541561663150787,
    0.06714903563261032,
    -0.004256050102412701,
    0.05138356238603592,
    -0.061394669115543365,
    0.06958435475826263,
    0.029510458931326866,
    0.006212680600583553,
    0.05935342609882355,
    0.06217789649963379,
    0.03869514539837837,
    0.016871990635991096,
    0.09106622636318207,
    0.01593017764389515,
    0.03309919685125351,
    3.424335227464326e-05,
    0.025418603792786598,
    -0.0019248499302193522,
    -0.04490964487195015,
    0.05094093829393387,
    -0.007762531749904156,
    0.0022712810896337032,
    -0.048982247710227966,
    0.04316263645887375,
    0.03385719656944275,
    -0.02204400859773159,
    -0.008660282008349895,
    -0.0358533076941967,
    0.11571227014064789,
    -0.11273631453514099,
    0.06849292665719986,
    -0.03595784679055214,
    0.04161537066102028,
    -0.013967745006084442,
    -0.004196549765765667,
    0.04396875202655792,
    0.07947150617837906,
    -0.038232240825891495,
    -0.004747415892779827,
    -0.012230468913912773,
    0.039619915187358856,
    -0.11451079696416855,
    0.0012758959783241153,
    -0.007560120429843664,
    0.015182306058704853,
    -0.039508406072854996,
    -0.06489536166191101,
    -0.003909661900252104,
    0.0037100922781974077,
    0.010909723117947578,
    -0.07211877405643463,
    0.024324269965291023,
    0.04425453022122383,
    0.02042572572827339,
    -0.07636857777833939,
    -0.03965488821268082,
    -0.04338192194700241,
    -0.10347922146320343,
    -0.04393737390637398,
    -0.01368421409279108,
    -1.568378671379378e-08,
    0.10027588903903961,
    -0.043567851185798645,
    0.050843071192502975,
    -0.08256983011960983,
    0.02588729001581669,
    0.056297384202480316,
    -0.010702059604227543,
    0.08518678694963455,
    0.02700129710137844,
    0.07154033333063126,
    -0.05953506380319595,
    0.0778793916106224,
    0.036633629351854324,
    0.08145243674516678,
    0.07252412289381027,
    -0.002973137190565467,
    -0.013765356503427029,
    -0.046995650976896286,
    -0.0247399490326643,
    -0.027804242447018623,
    -0.025088943541049957,
    -0.01294120866805315,
    -0.03852837160229683,
    0.11392410844564438,
    0.030737342312932014,
    -0.065057672560215,
    0.06248151883482933,
    -0.01869017630815506,
    0.02368609979748726,
    -0.0654701292514801,
    0.058893367648124695,
    0.06793640553951263,
    0.008447104133665562,
    0.015255128964781761,
    -0.04546090587973595,
    -0.04216332733631134,
    0.02343529835343361,
    -0.07064592838287354,
    0.01851677894592285,
    -0.006000120658427477,
    -0.025140153244137764,
    0.003474486293271184,
    -0.01600506715476513,
    0.0020763161592185497,
    0.010104725137352943,
    0.0021877381950616837,
    0.07691455632448196,
    0.008766746148467064,
    -0.012105572037398815,
    -0.047985345125198364,
    -0.012077542021870613,
    -0.02539162151515484,
    0.01326005533337593,
    -0.05451769009232521,
    -0.08339792490005493,
    0.052714310586452484,
    -0.011956708505749702,
    -0.01412263885140419,
    -0.05299930274486542,
    0.0125426622107625,
    0.12013623863458633,
    0.09160523116588593,
    0.12442110478878021,
    -0.03318800404667854,
]


def populate_neo4j(
    neo4j_driver: neo4j.Driver,
    neo4j_objs: dict[str, Any],
    should_create_vector_index: bool = False,
) -> neo4j.EagerResult:
    question_nodes = list(
        filter(lambda x: x["label"] == "Question", neo4j_objs["nodes"])
    )
    answer_nodes = list(filter(lambda x: x["label"] == "Answer", neo4j_objs["nodes"]))
    category_nodes = list(
        filter(lambda x: x["label"] == "Category", neo4j_objs["nodes"])
    )
    belongs_to_relationships = list(
        filter(lambda x: x["type"] == "BELONGS_TO", neo4j_objs["relationships"])
    )
    has_answer_relationships = list(
        filter(lambda x: x["type"] == "HAS_ANSWER", neo4j_objs["relationships"])
    )
    question_nodes_cypher = "UNWIND $nodes as node MERGE (n:Question {id: node.properties.id}) ON CREATE SET n = node.properties"
    answer_nodes_cypher = "UNWIND $nodes as node MERGE (n:Answer {id: node.properties.id}) ON CREATE SET n = node.properties"
    category_nodes_cypher = (
        "UNWIND $nodes as node MERGE (n:Category {id: node.id}) ON CREATE SET n = node"
    )
    belongs_to_relationships_cypher = "UNWIND $relationships as rel MATCH (q:Question {id: rel.start_node_id}), (c:Category {id: rel.end_node_id}) MERGE (q)-[r:BELONGS_TO]->(c)"
    has_answer_relationships_cypher = "UNWIND $relationships as rel MATCH (q:Question {id: rel.start_node_id}), (a:Answer {id: rel.end_node_id}) MERGE (q)-[r:HAS_ANSWER]->(a)"
    neo4j_driver.execute_query(question_nodes_cypher, {"nodes": question_nodes})
    neo4j_driver.execute_query(answer_nodes_cypher, {"nodes": answer_nodes})
    neo4j_driver.execute_query(category_nodes_cypher, {"nodes": category_nodes})
    neo4j_driver.execute_query(
        belongs_to_relationships_cypher, {"relationships": belongs_to_relationships}
    )
    res = neo4j_driver.execute_query(
        has_answer_relationships_cypher, {"relationships": has_answer_relationships}
    )

    if should_create_vector_index:
        vector_index_name = "vector-index-name"
        drop_index_if_exists(neo4j_driver, vector_index_name)
        # Create a vector index
        create_vector_index(
            neo4j_driver,
            vector_index_name,
            label="Question",
            embedding_property="vector",
            dimensions=384,
            similarity_fn="cosine",
        )

    return res


def build_data_objects(
    q_vector_fmt: Literal["neo4j", "qdrant"],
) -> tuple[dict[str, Any], list[Any]]:
    # read file from disk
    # this file is from https://github.com/weaviate-tutorials/quickstart/tree/main/data
    # MIT License
    file_name = "tests/e2e/data/jeopardy_tiny_with_vectors_all-MiniLM-L6-v2.json"
    with open(file_name, "r") as f:
        data = json.load(f)

    question_objs: list[Any] = []
    neo4j_objs: dict[str, list[Any]] = {"nodes": [], "relationships": []}

    # only unique categories and IDs for them
    unique_categories_list = list(set([c["Category"] for c in data]))
    unique_categories = [
        {"label": "Category", "name": c, "id": c} for c in unique_categories_list
    ]
    neo4j_objs["nodes"] += unique_categories

    for i, d in enumerate(data):
        id_ = hashlib.md5(d["Question"].encode()).hexdigest()
        question_properties = {
            "id": f"question_{id_}",
            "question": d["Question"],
        }

        if q_vector_fmt == "neo4j":
            # Store the vector directly on the question node for Neo4j
            question_properties["vector"] = d["vector"]

        # Add the question node
        neo4j_objs["nodes"].append(
            {
                "label": "Question",
                "properties": question_properties,
            }
        )
        # Add the answer node
        neo4j_objs["nodes"].append(
            {
                "label": "Answer",
                "properties": {
                    "id": f"answer_{id_}",
                    "answer": d["Answer"],
                },
            }
        )

        # Add relationships
        neo4j_objs["relationships"].append(
            {
                "start_node_id": f"question_{id_}",
                "end_node_id": f"answer_{id_}",
                "type": "HAS_ANSWER",
                "properties": {},
            }
        )
        neo4j_objs["relationships"].append(
            {
                "start_node_id": f"question_{id_}",
                "end_node_id": d["Category"],
                "type": "BELONGS_TO",
                "properties": {},
            }
        )

        # If Qdrant, we build PointStruct objects
        if q_vector_fmt == "qdrant":
            question_objs.append(
                models.PointStruct(
                    id=i,
                    payload={"neo4j_id": f"question_{id_}"},
                    vector=d["vector"],
                )
            )
        elif q_vector_fmt == "neo4j":
            # For Neo4j, the vector is already added to question_properties
            pass
        else:
            raise ValueError("q_vector_fmt must be either 'neo4j' or 'qdrant'")

    return neo4j_objs, question_objs


def populate_dbs(
    neo4j_driver: neo4j.Driver,
    qdrant_client: QdrantClient,
    collection_name: str = "Jeopardy",
) -> None:
    """
    Populates both Neo4j and Qdrant with the Jeopardy data set.
    """
    neo4j_objects, question_objs = build_data_objects("qdrant")

    # Recreate the Qdrant collection
    if qdrant_client.collection_exists(collection_name):
        qdrant_client.delete_collection(collection_name)

    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
    )

    _populate_qdrant(qdrant_client, question_objs, collection_name)
    populate_neo4j(neo4j_driver, neo4j_objects)


def _populate_qdrant(
    client: QdrantClient, question_objs: list[Any], collection_name: str
) -> None:
    """
    Inserts (upserts) question objects into the specified Qdrant collection.
    """
    client.upsert(
        collection_name=collection_name,
        points=question_objs,
    )


def main() -> None:
    """
    Entry point for running the database population script.
    """
    NEO4J_URL = "neo4j://localhost:7687"
    NEO4J_AUTH = ("neo4j", "password")

    with GraphDatabase.driver(NEO4J_URL, auth=NEO4J_AUTH) as neo4j_driver:
        qdrant_client = QdrantClient(url="http://localhost:6333")
        populate_dbs(neo4j_driver, qdrant_client, collection_name="Jeopardy")


if __name__ == "__main__":
    main()
