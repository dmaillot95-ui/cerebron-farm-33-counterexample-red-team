# CEREBRON — LEARNING MECHANISMS VALIDATION CAMPAIGN

Source: F08 targeted learning-mechanisms campaign, run 35806105920.
Epistemic status: UNREVIEWED_EXTERNAL_AGENT_OUTPUT. Do not treat F08 consensus as proof.

Claims/candidates to test independently:
1. Domain randomization / automatic domain randomization can improve robustness and sim-to-real transfer when the randomized training distribution covers relevant deployment variation.
2. DAgger-style interactive imitation and validated failure replay can improve a policy by concentrating new supervision on states induced by the current policy.
3. Policy/knowledge distillation can compress useful behavior into a smaller policy/model, but can lose capabilities and does not itself prove transfer.
4. Continual-learning replay/adapters may reduce catastrophic forgetting; this requires regression and transfer testing.
5. Curriculum, hard-example mining and active learning may improve sample efficiency when selection is informative rather than benchmark leakage.
6. Reversible LoRA/adapters are a candidate mechanism for CEREBRON G1 specialization, not yet demonstrated here.

CEREBRON transfer hypothesis:
validated task trajectories + audited RED/OPEN/REJECT corrections -> versioned curriculum -> reversible adapter -> cold held-out evaluation -> transfer evaluation -> ablation/regression -> F72/AFAH -> promote or rollback.

Required:
- distinguish documented mechanism from CEREBRON-specific extrapolation;
- identify dependencies/common-source contamination;
- actively seek counterexamples and failure regimes;
- no claim of trained six-AI weights;
- design measurable G0-vs-G1 tests with cold no-RAG, transfer no-RAG, with-RAG, ablation and regression;
- SYNTHETIC!=REAL; SIMULATION!=TEST; WORKFLOW_SUCCESS!=LEARNING; CLAIM<=EVIDENCE.
