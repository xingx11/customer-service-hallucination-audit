# Stage 2 Robustness Fixtures

These fixtures support Task 10 of the stage 2 plan. They live under `tests/fixtures/` so the default packaged dataset remains stable while later detector work can exercise harder boundary cases.

## Files

- `stage_2_robustness_replies.json`: reply cases using the same shape as `data/replies.json`.
- `stage_2_robustness_ground_truth.json`: human labels using the same shape as `data/ground_truth.json`.

## Coverage

| Case | Label | Focus |
| --- | --- | --- |
| `s2-policy-return-synonym` | 政策编造 | Synonym rewrite of 30-day return and shipping-fee fabrication. |
| `s2-policy-invoice-entry` | 政策偏差 | Wrong invoice channel and paper invoice promise. |
| `s2-parameter-bluetooth-synonym` | 参数编造 | Multiple parameter fabrications in one reply. |
| `s2-discount-student-synonym` | 优惠编造 | Student-discount wording absent from the policy. |
| `s2-information-return-address-synonym` | 信息编造 | Return-address fabrication without the exact stage 1 wording. |
| `s2-capability-logistics-synonym` | 能力越界 | Logistics lookup phrased as a successful internal query. |
| `s2-safety-pregnancy-paraphrase` | 安全误导 | Safety-sensitive advice that removes the doctor-consultation guardrail. |
| `s2-omission-size-feedback-paraphrase` | 信息遗漏 | Omits size-feedback caveats while giving a confident sizing answer. |
| `s2-negative-coupon-denial` | Non-hallucination | Hard negative with discount keywords used in a denial. |
| `s2-negative-invoice-policy` | Non-hallucination | Hard negative that repeats the paper-invoice limitation. |
| `s2-negative-logistics-boundary` | Non-hallucination | Hard negative that correctly refuses logistics lookup. |
| `s2-negative-safety-caution` | Non-hallucination | Hard negative that preserves the safety consultation requirement. |
