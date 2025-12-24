from istari.sources.clarity import ClaritySource

# Initialize Clarity source
clarity_source = ClaritySource()

# Get your API key from Clarity project settings:
# Settings > Data Export > Generate new API token
api_key = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjQ4M0FCMDhFNUYwRDMxNjdEOTRFMTQ3M0FEQTk2RTcyRDkwRUYwRkYiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiIxZDcwYTVjZS04ODg5LTQ1M2ItODFjYS1jMmJmNjcyOWQ3NmQiLCJzdWIiOiIzMDI3Mjk2NzU0MjU2OTAyIiwic2NvcGUiOiJEYXRhLkV4cG9ydCIsIm5iZiI6MTc2NTkxMTk5NiwiZXhwIjo0OTE5NTExOTk2LCJpYXQiOjE3NjU5MTE5OTYsImlzcyI6ImNsYXJpdHkiLCJhdWQiOiJjbGFyaXR5LmRhdGEtZXhwb3J0ZXIifQ.lt2HaiZucAH-hE6teUFzlVruWZVGGBsb4AP9KQh0bRRvUt2eb8PT3l_UauG2XZkKgv3ODpP4Lx5BekMn3VgglLLc_FJyCy7SddoYXoe0RAdEDI_BS-7Gbv9YXeE7en14cbNRi9YvtdBbGsdkqtNOp1EXU9fuUVtxwt_p5O4HivJbYLa1v10lhcoYLMxpiOMuhNSUXafjhtjRvDA44lVGJFrKbav3b6SL87Zm4RevTTi68wE83nYqUwkjaj2f_-8TEfes8Uat6_tOWmb586iN_2p1KuqDuSD4ffZUXFQyJmVIDg4VSGbF6iUlabBHzfT1vdGtjCSAKaC0WS0Re9vlrQ"
project_id = "ugr10r6pdy"

# Fetch from API and process
events, signals = clarity_source.import_from_api(
    api_key=api_key,
    project_id=project_id,
    start_date="2025-10-01",  # Optional: filter by date range
    end_date="2025-12-01",    # Optional: filter by date range
)

print(f"Imported {len(events)} events")
print(f"Signals: {signals}")