# TEST CASE TASK 6 - SCRIPT CLASSIFIER



### 1. FUNCTIONAL TESTING
| TC ID | Mô tả                          | Input                            | Expected Output                    | Ghi chú       |
| ----- | ------------------------------ | -------------------------------- | ---------------------------------- | ------------- |
| FT01  | Phân loại câu tích cực cơ bản  | “dạy rất hay”                    | Positive                           | POS vocab     |
| FT02  | Phân loại câu tiêu cực cơ bản  | “dở”                             | Negative                           | NEG vocab     |
| FT03  | Câu có cả positive và negative | “dạy hay nhưng dở”               | Negative                           | score = 0/-   |
| FT04  | Batch prediction               | ["dạy rất hay","dở","không tốt"] | ["Positive","Negative","Negative"] | predict_batch |
| FT05  | Input rỗng                     | ""                               | Negative                           | score = 0     |


### 2. DATA VALIDATION TESTING

| TC ID | Mô tả                               | Input                  | Expected Output    | Ghi chú              |
| ----- | ----------------------------------- | ---------------------- | ------------------ | -------------------- |
| DV01  | Kiểm tra tokenization output hợp lệ | “dạy quá chán”         | List tokens hợp lệ | không crash          |
| DV02  | POS vocab hoạt động đúng            | “hay”                  | Positive           | token ∈ pos_vocab    |
| DV03  | NEG vocab hoạt động đúng            | “dở”                   | Negative           | token ∈ neg_vocab    |
| DV04  | Bật stopwords removal               | “môn học này quá chán” | Positive/Negative  | không crash          |
| DV05  | Protected words không bị remove     | “không tốt”            | Negative           | “không” được giữ lại |
| DV06  | Vocab file hợp lệ                   | load JSON              | dict               | JSON parse đúng      |

### 3. EDGE CASE TESTING

| TC ID | Mô tả               | Input                       | Expected Output | Ghi chú       |
| ----- | ------------------- | --------------------------- | --------------- | ------------- |
| EC01  | Chuỗi rỗng          | ""                          | Negative        | default case  |
| EC02  | Chỉ stopwords       | “và là của trong”           | Negative        | không vocab   |
| EC03  | Unknown words       | “abc xyz qwe”               | Negative        | no match      |
| EC04  | Noise punctuation   | “!!! hay ???”               | Positive        | lọc token     |
| EC05  | Double negation     | “không không tốt”           | Positive        | logic kỳ vọng |
| EC06  | Negation + positive | “không hay”                 | Negative        | đảo nghĩa     |
| EC07  | Text nhiễu + vocab  | “@@ dạy hay ## nhưng dở !!” | Negative        | mixed         |
