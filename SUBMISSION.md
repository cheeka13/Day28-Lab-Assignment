# Hướng Dẫn Nộp Bài - Lab #28: Full Platform Integration Sprint

## Yêu Cầu Nộp Bài

**Full AI infrastructure platform demo** - từ data ingestion đến model serving với full observability.

## Các Artifacts Cần Nộp

### 1. Source Code
- Folder `lab28/` hoàn chỉnh với tất cả files
- Tất cả integration scripts hoạt động
- Prefect flows đã deploy và schedule

### 2. Screenshots Demo
Chụp màn hình các bước:
- Prefect UI: http://localhost:4200 (flow đang chạy)
- API Gateway call: `curl http://localhost:8000/health`
- Grafana dashboard: http://localhost:3000

### 3. Kết Quả Smoke Tests
Chạy và chụp màn hình kết quả:
```bash
cd lab28
pytest smoke-tests/ -v
```
Kỳ vọng: 5/5 tests passing

### 4. Production Readiness Score
```bash
python scripts/production_readiness_check.py
```
Kỳ vọng: Score >80%

### 5. Documentation
- `README.md` giải thích cách:
  - Start platform: `docker compose up -d`
  - Deploy Prefect flows
  - Run smoke tests
  - Access dashboards (Grafana:3000, Prometheus:9090, Prefect:4200)

## Định Dạng Nộp Bài

Tạo Repo GitHub chứa:
```
lab28_submission_[student_id]
├── lab28/                    # Source code hoàn chỉnh
│   ├── docker-compose.yml
│   ├── prefect/flows/
│   ├── scripts/
│   ├── api-gateway/
│   └── monitoring/
├── screenshots/              # Screenshots demo
│   ├── prefect_ui.png
│   ├── api_gateway.png
│   └── grafana_dashboard.png
├── smoke_tests_results.png   # Screenshot kết quả pytest
├── production_readiness.png  # Screenshot readiness score
└── README.md                # Hướng dẫn setup
```

## Địa Điểm Nộp
Nộp link repo GitHub qua LMS

## Tiêu Chí Chấm Điểm

| Tiêu Chí | Trọng Số | Mô Tả |
|----------|----------|-------|
| Integration Completeness | 40% | Tất cả 10 integration points hoạt động, data flow end-to-end |
| Observability | 25% | Logs, metrics, traces hiển thị; alerts configured |
| Performance | 20% | Latency trong SLO; load tested; không có memory leaks |
| Architecture Quality | 15% | Clean separation, GitOps config, documented decisions |

## Các Vấn Đề Cần Tránh

- Config drift giữa các environments
- Thiếu error handling tại integration points
- Monitoring coverage không hoàn chỉnh
- Không có rollback strategy
- Demo không test trước khi nộp

## 5 Câu Hỏi Cần Trả Lời Khi Nộp

1. **Phân tích các trade-offs trong thiết kế kiến trúc AI platform của bạn. Bạn đã cân bằng giữa performance, reliability, và maintainability như thế nào?**
   - **Performance vs Cost/Resource (Cân bằng hiệu năng):** Để tối ưu tài nguyên máy cá nhân, hệ thống sử dụng kiến trúc Hybrid. LLM (Qwen2.5-7B-Instruct-GPTQ-Int4) và mô hình Embedding (bge-small-en-v1.5) đòi hỏi năng lực tính toán GPU lớn được đẩy lên môi trường đám mây Kaggle GPU T4. Ngược lại, Feast Redis Online Store được cấu hình tại Local để đạt độ trễ truy xuất đặc trưng sub-millisecond (< 1ms). Điều này đảm bảo tốc độ suy luận nhanh mà không tốn chi phí hạ tầng đắt đỏ.
   - **Reliability (Độ tin cậy):** Việc tích hợp Kafka làm vùng đệm tin nhắn (message broker) giúp cô lập hệ thống khỏi việc mất mát dữ liệu khi chịu tải cao đột biến (spikes). Các điểm tích hợp (Integration points) đều được bọc trong các cơ chế xử lý lỗi ngoại lệ chặt chẽ, cho phép hệ thống tự phục hồi hoặc hạ cấp chức năng một cách có kiểm soát khi có lỗi ngoại vi.
   - **Maintainability (Khả năng bảo trì):** Kiến trúc phân lớp rõ ràng (Separation of Concerns). Toàn bộ luồng ETL, biến đổi đặc trưng và lập chỉ mục (Kafka → Prefect → Delta Lake → Feast/Qdrant) được tách biệt hoàn toàn khỏi luồng suy luận phục vụ trực tiếp (FastAPI API Gateway → vLLM). Điều này giúp các kỹ sư ML và Data Engineers dễ dàng nâng cấp, kiểm thử và vá lỗi từng service độc lập mà không ảnh hưởng đến phần còn lại.

2. **Trong kiến trúc hybrid (Local + Kaggle), bạn xử lý ngắt kết nối giữa local và Kaggle như thế nào? Có cơ chế fallback không?**
   - **Xử lý ngắt kết nối & Phát hiện sự cố:** API Gateway sử dụng các kết nối HTTP bất đồng bộ thông qua `httpx.AsyncClient` có cấu hình thời gian chờ (`timeout=30` đối với vLLM suy luận và `timeout=5` đối với Embedding). Nếu kết nối bị đứt hoặc cổng ngrok/cloudflare tunnel bị ngắt, API Gateway sẽ bắt các ngoại lệ kết nối (`ConnectError`, `TimeoutException`).
   - **Cơ chế Fallback thông minh:**
     - *Local Embedding Fallback:* Nếu Kaggle Embedding API gặp sự cố, hệ thống có thể kích hoạt fallback sang mô hình sentence-transformers gọn nhẹ chạy trực tiếp bằng CPU nội bộ để tạo vector embedding truy vấn.
     - *RAG Degradation:* Khi vector store (Qdrant) hoặc LLM (vLLM) bị mất kết nối, thay vì trả về lỗi HTTP 500, Gateway sẽ trả về kết quả fallback thân thiện với người dùng (ví dụ: sử dụng dữ liệu câu hỏi thường gặp đã cache cục bộ hoặc đưa ra cảnh báo hệ thống đang bảo trì tạm thời).
     - *Circuit Breaker:* Ngăn chặn việc liên tục gửi các request lỗi dồn dập lên Kaggle khi tunnel đã sập, giúp tiết kiệm tài nguyên và bảo vệ hệ thống tránh bị quá tải khi kết nối hồi phục.

3. **Giải thích cách event-driven architecture với Kafka giúp decouple các components trong AI platform của bạn.**
   - **Decoupling về mặt thời gian (Temporal Decoupling):** Hệ thống Data Ingestion đẩy dữ liệu thô trực tiếp vào Kafka topic `data.raw` và nhận phản hồi thành công ngay lập tức. Luồng Ingestion không cần quan tâm khi nào Prefect chạy, hay mất bao lâu để vectorize và đánh chỉ mục dữ liệu. Kafka lưu trữ bền vững (message persistence) các bản ghi này cho đến khi Prefect Flow sẵn sàng xử lý.
   - **Decoupling về mặt logic (Logical Decoupling):** API Gateway và Data Ingestion Service hoàn toàn không biết đến sự tồn tại của Feast, Delta Lake hay Qdrant. Các thành phần này giao tiếp hoàn toàn gián tiếp qua các sự kiện dữ liệu trong Kafka.
   - **Khả năng mở rộng và Hỗ trợ nhiều Consumer (Multi-consumer Support):** Chủ đề `data.raw` có thể được đăng ký tiêu thụ bởi nhiều service độc lập cùng lúc: một Prefect pipeline để lưu vào Delta Lake thô, một stream-processing engine để phát hiện gian lận thời gian thực, và một monitoring consumer để thống kê số lượng bản ghi thô. Tất cả đều diễn ra song song mà không làm chậm hệ thống gửi tin gốc.

4. **Bạn đã implement observability như thế nào? Logs, metrics, và traces được thu thập và visualized ra sao?**
   - **Metrics (Thống kê định lượng):** API Gateway được tích hợp thư viện `prometheus-fastapi-instrumentator`. Mọi request đi qua cổng đều được đo đạc tự động về số lượng (request count), độ trễ (latency histogram) và mã trạng thái trả về (status code). Prometheus Server sẽ định kỳ "scrape" (thu thập) các metrics này tại cổng `http://localhost:8000/metrics`. Grafana được kết nối trực tiếp với Prometheus làm Data Source để trực quan hóa dữ liệu qua các biểu đồ động như P95 Latency, QPS, Error Rate.
   - **Logs (Nhật ký hệ thống):** Logs được cấu trúc hóa rõ ràng, hiển thị đầy đủ thời gian thực thi, các bước xử lý nghiệp vụ chính (Ingest, Consumer, Search, Inference) và chi tiết lỗi hệ thống khi có ngoại lệ xảy ra.
   - **Traces (Dấu vết thực thi):** Hệ thống tích hợp LangSmith Tracing SDK. Khi API Gateway thực hiện một quy trình RAG (Vector Search → LLM Generation), LangSmith sẽ ghi nhận chi tiết thời gian chạy của từng mắt xích độc lập, các prompt đầu vào và câu trả lời đầu ra, cho phép các kỹ sư dễ dàng quan sát, tối ưu hóa câu lệnh và phát hiện điểm nghẽn hiệu năng (bottleneck).

5. **Nếu một service trong stack (ví dụ: Qdrant hoặc Kafka) bị crash, hệ thống của bạn sẽ xử lý như thế nào? Có graceful degradation không?**
   - **Khi Qdrant (Vector Store) bị crash:** API Gateway sẽ bắt lỗi kết nối HTTP đến cổng `6333`. Thay vì dừng hoạt động, Gateway thực hiện hạ cấp dịch vụ gracefully bằng cách bỏ qua bước tìm kiếm ngữ cảnh bổ sung (RAG) và chuyển thẳng câu hỏi gốc của người dùng tới LLM, hoặc sử dụng cơ chế tìm kiếm từ khóa đơn giản (Lexical Search) trên cơ sở dữ liệu Feast/SQL cục bộ để cung cấp ngữ cảnh cơ bản nhất có thể.
   - **Khi Kafka (Event Broker) bị crash:** Dịch vụ Data Ingestion sẽ ghi nhận lỗi mất kết nối đến cổng `9092`. Để tránh mất dữ liệu thô, Ingestion script sẽ tạm thời ghi dữ liệu vào một file log đệm cục bộ (Local backup/buffer file). Ngay khi Kafka hoạt động trở lại, một tiến trình daemon sẽ tự động đẩy bù các dữ liệu đệm này vào topic `data.raw` (Reliable Ingestion).
   - **Khi Feast/Redis bị crash:** Tiến trình Prefect Flow sẽ ghi nhận lỗi ghi đặc trưng trực tuyến (online feature store), tuy nhiên luồng dữ liệu thô vẫn được lưu trữ an toàn trong Delta Lake dưới định dạng Parquet. Khi Feast hồi phục, hệ thống chỉ cần chạy lại một tác vụ đồng bộ hóa để cập nhật đầy đủ các đặc trưng còn thiếu từ Delta Lake sang Redis trực tuyến.


## Câu Hỏi Thêm?
Liên hệ giảng viên qua LMS hoặc office hours.
