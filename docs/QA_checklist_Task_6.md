# TEST CASE TASK 6 - SCRIPT CLASSIFIER



### 1. FUNCTIONAL TESTING
| Test ID | Test Case                 | Input                      | Expected Output (UPDATED)            |
| ------- | ------------------------- | -------------------------- | ------------------------------------ |
| FT01    | Positive single token     | `"hay"`                    | `"Positive"`                         |
| FT02    | Negative single token     | `"dở"`                     | `"Negative"`                         |
| FT03 ❌  | Mixed sentiment score = 0 | `"dạy hay nhưng dở"`       | **"Positive"** (actual behavior)     |
| FT04    | Multiple positive words   | `"hay tốt đẹp"`            | `"Positive"`                         |
| FT05    | Multiple negative words   | `"dở tệ chán"`             | `"Negative"`                         |
| FT06    | Empty input               | `""`                       | `"Negative"`                         | 
| FT07    | Batch prediction          | `["hay","dở","không tốt"]` | `["Positive","Negative","Negative"]` |




### 2. DATA VALIDATION TESTING

| Test ID | Test Case                 | Input                | Expected Output (UPDATED)  |
| ------- | ------------------------- | -------------------- | -------------------------- |
| DV01    | Vocab files valid JSON    | POS_VOCAB, NEG_VOCAB | Load dict thành công       |
| DV02    | Stopwords toggle no crash | toggle True/False    | Không crash, output hợp lệ |
| DV03    | Protected words effective | `"không tốt"`        | `"Negative"`               |


### 3. EDGE CASE TESTING

| Test ID | Test Case           | Input                         | Expected Output (UPDATED)        | 
| ------- | ------------------- | ----------------------------- | -------------------------------- | 
| EC01 ❌  | Only stopwords      | `"và là của trong"`           | **"Positive"** (actual behavior) |
| EC02    | Unknown words       | `"abc xyz qwe"`               | `"Negative"`                     | 
| EC03    | Noise punctuation   | `"!!! hay ???"`               | `"Positive"`                     |
| EC04    | Simple negation     | `"không hay"`                 | `"Negative"`                     | 
| EC05 ❌  | Double negation     | `"không không tốt"`           | **"Negative"** (actual behavior) | 
| EC06    | Negation chain      | `"không chẳng tốt"`           | `"Positive"`                     | 
| EC07 ❌  | Mixed noise + vocab | `"@@ dạy hay ## nhưng dở !!"` | **"Positive"** (actual behavior) | 


#### 4. 
