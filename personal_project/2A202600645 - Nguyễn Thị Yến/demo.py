import json
from pathlib import Path
from src.task10_generation import generate_with_citation

dataset = json.loads(Path("evaluation/golden_dataset.json").read_text(encoding="utf-8"))

for i, item in enumerate(dataset, 1):
    result = generate_with_citation(item["question"])
    print("=" * 80)
    print(f"Q{i}: {item['question']}")
    print(f"Expected: {item['expected_answer']}")
    print(f"Actual: {result['answer']}")
    print(f"Sources: {[s.get('metadata', {}).get('source') for s in result['sources']]}")