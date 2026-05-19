# NegConstraint query formulation labels

Two label sets are included.

## 1) Textual-semantic reading
This labels each query by the wording of the query itself. Counts do not match the paper table, because several query strings are ambiguous or visibly inconsistent with the three formal templates.

- A - a: 132 queries
  - IDs: 0-2, 4, 7-10, 12-15, 17, 21-22, 28, 31, 33-43, 45-50, 54, 56, 62, 65-66, 70, 72, 74-78, 87, 92, 95, 99, 102, 104, 110, 117, 127, 136, 141, 145-146, 154, 161-163, 167, 172, 181, 191, 201, 210, 228-229, 236, 246, 256, 265, 273, 281, 290, 295, 305, 314-365
- (A - a) ∪ B: 90 queries
  - IDs: 3, 5-6, 11, 16, 18-20, 23-27, 29-30, 32, 44, 51-53, 55, 57-61, 63-64, 67-69, 71, 73, 79-86, 88-91, 93-94, 96-98, 100-101, 103, 105-109, 111-116, 118-126, 128-135, 137-140, 142-144, 147, 293
- (A - a) ∪ (B - b): 144 queries
  - IDs: 148-153, 155-160, 164-166, 168-171, 173-180, 182-190, 192-200, 202-209, 211-227, 230-235, 237-245, 247-255, 257-264, 266-272, 274-280, 282-289, 291-292, 294, 296-304, 306-313

## 2) Paper-count-aligned best fit
This version forces the counts from the paper table: 136 / 123 / 107. Treat it as a count-aligned best fit rather than purely surface-semantic labels.

- A - a: 136 queries
  - IDs: 0-15, 17, 21-22, 28, 31, 33-43, 45-50, 54-56, 62, 65-66, 69-70, 72, 74-78, 87, 92, 95, 99, 102, 104, 110, 117, 127, 136, 141, 145-146, 154, 163, 167, 172, 181, 191, 201, 210, 228-229, 236, 246, 256, 265, 273, 281, 290, 295, 305, 314-365
- (A - a) ∪ B: 123 queries
  - IDs: 16, 18-20, 23-27, 29-30, 32, 44, 51-53, 57-61, 63-64, 67-68, 71, 73, 79-86, 88-91, 93-94, 96-98, 100-101, 103, 105-109, 111-116, 118-126, 128-135, 137-140, 142-144, 147, 269-272, 274-280, 282-289, 291-294, 296-304, 306-313
- (A - a) ∪ (B - b): 107 queries
  - IDs: 148-153, 155-162, 164-166, 168-171, 173-180, 182-190, 192-200, 202-209, 211-227, 230-235, 237-245, 247-255, 257-264, 266-268

## Notes
- Query ID 4 has no explicit negative-constraint phrase in the query text, so it is assigned to the nearest single-topic formulation in both versions.
- Query IDs such as 271 explicitly contain A/a/B/b-style wording, so the textual-semantic version places them in (A - a) ∪ (B - b). The count-aligned version may place some such late IDs differently to preserve the paper's stated counts.
