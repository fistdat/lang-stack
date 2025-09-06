# EAIO Energy AI Optimizer - LLM as Judge Evaluator Setup

## Tổng quan về LLM as Judge

LLM as Judge là phương pháp đánh giá chất lượng của ứng dụng LLM bằng cách sử dụng chính AI model để chấm điểm và đưa ra lý do về các đầu ra. Phương pháp này có khả năng mở rộng, hiệu quả về chi phí và cung cấp các đánh giá "giống con người" với các tiêu chí phức tạp.

## Đề xuất Setup Evaluator cho EAIO

Dựa trên đặc thù của hệ thống EAIO (Energy AI Optimizer) là một multi-agent system tối ưu hóa năng lượng, tôi đề xuất sử dụng **8 evaluator chính** sau:

### 1. EVALUATOR CỐT LÕI (CORE) 🎯

#### 1.1 Correctness
- **Mục đích**: Đánh giá tính chính xác tổng thể của các khuyến nghị tối ưu hóa năng lượng
- **Ứng dụng**: Đảm bảo tính chính xác về mặt factual của các phân tích tiêu thụ năng lượng, tính toán tiết kiệm, và khuyến nghị
- **Điểm số**: 0-1 (càng gần 1 càng tốt)

#### 1.2 Contextcorrectness  
- **Mục đích**: Đánh giá tính chính xác dựa trên dữ liệu năng lượng và context được cung cấp
- **Ứng dụng**: Kiểm tra xem các khuyến nghị có phù hợp với dữ liệu tiêu thụ năng lượng thực tế hay không
- **Điểm số**: 0-1 (càng gần 1 càng tốt)

#### 1.3 Relevance
- **Mục đích**: Đánh giá mức độ liên quan của câu trả lời với câu hỏi về tối ưu hóa năng lượng
- **Ứng dụng**: Đảm bảo các agent trả lời đúng vấn đề được đặt ra về năng lượng
- **Điểm số**: 0-1 (càng gần 1 càng tốt)

#### 1.4 Helpfulness
- **Mục đích**: Đánh giá mức độ hữu ích của các khuyến nghị tối ưu hóa năng lượng
- **Ứng dụng**: Kiểm tra xem các giải pháp có thực sự giúp người dùng tiết kiệm năng lượng không
- **Điểm số**: 0-1 (càng gần 1 càng tốt)

### 2. EVALUATOR CHUYÊN BIỆT (SPECIALIZED) 🔬

#### 2.1 Hallucination
- **Mục đích**: Phát hiện thông tin về năng lượng bịa đặt hoặc không có cơ sở
- **Ứng dụng**: Critical cho EAIO - tránh đưa ra thông tin sai về tiêu thụ năng lượng hoặc khuyến nghị không chính xác
- **Điểm số**: 0-1 (0 = không có hallucination, 1 = có hallucination nghiêm trọng)

#### 2.2 Contextrelevance
- **Mục đích**: Đánh giá mức độ liên quan của dữ liệu năng lượng được retrieve với câu hỏi
- **Ứng dụng**: Tối ưu hóa retrieval system cho dữ liệu năng lượng, đảm bảo RAG system hoạt động hiệu quả
- **Điểm số**: 0-1 (càng gần 1 càng tốt)

#### 2.3 Faithfulness
- **Mục đích**: Đánh giá tính trung thực với dữ liệu nguồn về năng lượng
- **Ứng dụng**: Đảm bảo các báo cáo và khuyến nghị faithful với dữ liệu tiêu thụ năng lượng thực tế
- **Điểm số**: 0-1 (càng gần 1 càng tốt)

#### 2.4 Conciseness
- **Mục đích**: Đánh giá tính súc tích của các khuyến nghị và báo cáo
- **Ứng dụng**: Đảm bảo thông tin được truyền đạt ngắn gọn, dễ hiểu cho người dùng cuối
- **Điểm số**: 0-1 (càng gần 1 càng tốt)

### 3. EVALUATOR BỔ SUNG (OPTIONAL) 📊

#### 3.1 Goal Accuracy (Recommended)
- **Mục đích**: Đánh giá mức độ đạt được mục tiêu tối ưu hóa năng lượng cụ thể
- **Ứng dụng**: Đo lường success rate trong việc hoàn thành các task tối ưu hóa năng lượng
- **Điểm số**: 0-1 (càng gần 1 càng tốt)

#### 3.2 Topic Adherence Classification (Optional)
- **Mục đích**: Phân loại mức độ tuân thủ chủ đề năng lượng
- **Ứng dụng**: Đảm bảo các agent không đi lạc khỏi chủ đề tối ưu hóa năng lượng
- **Điểm số**: Pass/Fail hoặc classification score

## Cấu hình Implementation

### Setup Steps:

```python
# 1. Core Evaluators (Bắt buộc)
core_evaluators = [
    "correctness",
    "contextcorrectness", 
    "relevance",
    "helpfulness"
]

# 2. Specialized Evaluators (Khuyến nghị cao)
specialized_evaluators = [
    "hallucination",
    "contextrelevance", 
    "faithfulness",
    "conciseness"
]

# 3. Optional Evaluators (Tùy chọn)
optional_evaluators = [
    "goal_accuracy",
    "topic_adherence_classification"
]
```

### Variable Mapping cho EAIO:
```json
{
  "input": "user_query",
  "output": "agent_response", 
  "context": "energy_data_context",
  "expected_output": "ground_truth_solution",
  "goal": "energy_optimization_target"
}
```

### Evaluation Frequency:
- **Real-time evaluation**: Core evaluators (correctness, relevance, helpfulness)
- **Batch evaluation**: Specialized evaluators (hallucination, faithfulness) - chạy hàng ngày
- **Periodic evaluation**: Optional evaluators - chạy hàng tuần

## Lợi ích cho EAIO System:

1. **Đảm bảo chất lượng**: Tự động kiểm tra tính chính xác của khuyến nghị năng lượng
2. **Phát hiện lỗi sớm**: Hallucination detection ngăn chặn thông tin sai lệch
3. **Tối ưu hóa hiệu suất**: Context evaluation cải thiện RAG system
4. **Trải nghiệm người dùng**: Helpfulness và conciseness đảm bảo UX tốt
5. **Tuân thủ mục tiêu**: Goal accuracy tracking đảm bảo system hoạt động đúng mục đích

## Metrics và Thresholds:

| Evaluator | Target Score | Warning Threshold | Critical Threshold |
|-----------|--------------|-------------------|-------------------|
| Correctness | ≥ 0.85 | < 0.7 | < 0.5 |
| Contextcorrectness | ≥ 0.8 | < 0.65 | < 0.45 |
| Relevance | ≥ 0.9 | < 0.75 | < 0.6 |
| Helpfulness | ≥ 0.85 | < 0.7 | < 0.5 |
| Hallucination | ≤ 0.1 | > 0.2 | > 0.35 |
| Contextrelevance | ≥ 0.8 | < 0.65 | < 0.45 |
| Faithfulness | ≥ 0.9 | < 0.8 | < 0.65 |
| Conciseness | ≥ 0.75 | < 0.6 | < 0.4 |

## Monitoring và Alerting:

- **Dashboard real-time**: Hiển thị điểm số của các evaluator chính
- **Alert system**: Cảnh báo khi điểm số xuống dưới warning threshold
- **Weekly reports**: Báo cáo tổng hợp performance của toàn bộ system
- **Trend analysis**: Phân tích xu hướng cải thiện/suy giảm theo thời gian

---

*Tài liệu này được tạo để hỗ trợ việc setup LLM as Judge evaluators cho hệ thống EAIO Energy AI Optimizer sử dụng Langfuse.*