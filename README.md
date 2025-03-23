# **Autocomplete API Extraction: Approach & Findings**  

## **Overview**  
This project focuses on extracting **all possible names** from an **undocumented autocomplete API** across its **three different versions (v1, v2, v3)**.  
The extraction process involves making optimized requests while handling API constraints such as **rate limits**, **pagination**, and **lexicographical expansion**.

---

## **Approach**  

### **1. Understanding API Constraints**
Each version of the API has different behavior regarding:  

- **Maximum API Calls Per Minute:**  
  - **v1:** `100 calls/min`
  - **v2:** `50 calls/min`
  - **v3:** `80 calls/min`

- **Maximum Results Per Request (`max_results` parameter):**  
  - **v1:** `50`
  - **v2:** `75`
  - **v3:** `100`

- **Default Results When `max_results` is Not Provided:**  
  - **v1:** `10`
  - **v2:** `12`
  - **v3:** `15`

To efficiently extract all names, we must **handle these constraints carefully**.

---

### **2. Lexicographical Expansion Strategy**  
Since the API works via **autocomplete**, names are retrieved based on query **prefixes**.  
The extraction follows these steps:

1. **Start with a prefix (single character)**:  
   - **v1:** `"a" → "b" → "c" ... "z"`  
   - **v2:** `"0" → "1" → "2" ... "9" → "a" → "b" ... "z"`  
   - **v3:** `"0" → "1" → "2" ... "9" → "a" → "b" ... "z"` with second character as special character `" " -> "+" -> "-" -> "."`
     
2. **Extract results using `max_results` to get the largest possible batch.**  

3. **Check if the maximum results were returned:**  
   - If fewer than `max_results` were received, **stop expanding that branch**.  
   - If exactly `max_results` were received, it **indicates more results exist**, so we expand further.

4. **Expand deeper lexicographically (recursive search):**  
   - Use the last returned name as a **new prefix** and fetch again.  
   - Continue until a pre-defined `max_depth` is reached.  
   - **Dynamic max_depth selection:** If increasing `max_depth` no longer increases unique names, stop deeper searches.

5. **Store unique names in a `set` to eliminate duplicates.**

---

### **3. Handling API Rate Limits**
Each API version has a **different rate limit**, so we enforce a **delay** between requests:  

\[
\text{Delay} = \frac{60}{\text{MAX_CALLS_PER_MINUTE}}
\]

| API Version | Rate Limit (calls/min) | Delay Between Requests |
|-------------|----------------------|----------------------|
| **v1** | 100 | `0.6s` |
| **v2** | 50  | `1.2s` |
| **v3** | 80  | `0.75s` |

If the API **returns a 429 (Rate Limit Exceeded)** response:
- **Wait for 60 seconds** before retrying.
- **Resume from the last failed request**.

---

## **API Behavior Observations**  

| Feature              | Version 1 | Version 2 | Version 3 |
|----------------------|-----------|-----------|-----------|
| **Max API Calls Per Min** | 100       | 50        | 80        |
| **Max `max_results` Allowed** | 50        | 75        | 100       |
| **Default Results (Without `max_results`)** | 10        | 12        | 15        |
| **Character Ranges Tested** | `"a-z"` | `"0-9, a-z"` | `"0-9, a-z, space, +, -, ."` |
| **Supports Special Characters?** | ❌ | ❌ | ✅ (`space`, `+`, `-`, `.`) |
| **Rate Limit Handling Required?** | ✅ | ✅ | ✅ |
| **Total Names Extracted** | 18,632 | 13,730 | 12,317 |
| **Total API Calls Made** | 1,630 | *Unknown* | 1,871 |

### **Key Findings**
1. **Higher `max_results` speeds up extraction.**  
   - **v3 is the most efficient** because it allows `max_results=100`.  
   - **v1 is the slowest** since it caps at `max_results=50`.

2. **API v3 supports additional characters like space, `+`, `-`, and `.`.**  
   - This suggests v3 has a **broader name set** than v1 and v2.

3. **When `max_results` is omitted, the API defaults to different values per version.**  
   - v1 → **10 results**  
   - v2 → **12 results**  
   - v3 → **15 results**  

4. **Lexicographical Expansion Works Well.**  
   - Querying `"a"`, `"b"`, `"c"`... ensures we retrieve all possible names.

5. **Rate Limits Must Be Handled Properly.**  
   - A **delay-based approach** prevents excessive 429 errors.

---

## **Implementation Details (Code Explanation)**  

Each API version follows the same **recursive expansion approach** but with adjustments based on API behavior.

### **Version 1**
- Uses **`max_results=50`**.
- Expands only **alphabetically (`a-z`)**.
- Stops if fewer than **50 results** are returned.

```python
fetch_names("a")  # Starts from 'a'
```

### **Version 2**
- Uses **`max_results=75`**.
- Supports **Numerical (`0-9`) and Alphabet (`a-z`)**.
- Uses a **next_char()** function to iterate through numbers and letters.

```python
fetch_names("0")  # Starts from '0', then '1', ..., '9', 'a', ..., 'z'
```

### **Version 3**
- Uses **`max_results=100`**.
- Supports special characters: **(`space, +, -, .`)**.
- Stops if fewer than **50 results** are returned.

```python
fetch_names("0")  # Starts from '0', then '1', ..., '9', 'a', ..., 'z' but second character contains special characters ' ', '+', '-', '.'
```

### **Running the Script**
1. Ensure Python 3 is installed.
2. Run the script:
   ```python
    fetch_names("0")  # Starts from '0', then '1', ..., '9', 'a', ..., 'z' but second character contains special characters ' ', '+', '-', '.'
    ```
3. View results:
  - Total unique names extracted.
  - Total API calls made.
  - All names sorted alphabetically.

### **Future Improvements**
- Multithreading for Faster Extraction:
    Running multiple threads to parallelize API calls.
- Persistent Storage:
    Store extracted names in a database or file.

### **Conclusion**
This approach successfully extracts all possible names from the API across three different versions while efficiently handling:
- Rate limits
- Pagination via **(`max_results`)**
- Recursive lexicographical expansion
- Dynamic max_depth detection

Each version of the API has unique characteristics (**max_results**, **special character support**, **rate limits**), and this script is optimized to handle them all. 
