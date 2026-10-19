# AgriRobot 0.3 — الذكاء المحلي

هذه صورة تطوير amd64 للحاسوب، وليست firmware للمتحكم. يبني workflow الصورة مع الأوزان والمحركات ويمنع تغليفها إن فشل اختبار الاستدلال المعزول عن الشبكة. نتائج التشغيل الفعلية في offline-inference-report.json، والإقلاع في boot-validation.json بجوار ISO. لا تعتبر النسخة مجتازة قبل نجاحهما.

## المثبت داخل الصورة عند نجاح البناء

- Qwen3-0.6B Q4_0، محادثة عامة متعددة اللغات تشمل العربية، عبر llama.cpp b6000؛ Apache-2.0 للأوزان وMIT للمحرك.
- Whisper tiny متعدد اللغات، تحويل الصوت إلى نص عبر whisper.cpp v1.7.5؛ MIT. الاختبار المرجعي بالإنجليزية؛ دقة اللهجات العربية غير مقاسة.
- YOLO11n، كاشف COCO عام بصيغة ONNX مع ONNX Runtime 1.23.2. ليس نموذج تشخيص أمراض أو مصنف حشرات. الأصل والتصدير تحت AGPL-3.0، وتبقى ملفات المصدر والإشعارات مرفقة.
- eSpeak NG للصوت العربي الصناعي الخفيف؛ ليس صوتًا عصبيًا. Piper غير مثبت بسبب عدم حسم ترخيص مجموعة بيانات الصوت المختار.
- أرشيف PlantDoc الكامل المتحقق، 2578 صورة، و33 صورة مرجعية مختارة مع النسب والمصادر. وجود الصور لا يعني أن نموذجًا قد تدرب عليها.
- مصادر محركي llama.cpp وwhisper.cpp المثبتة بالـ commit وSHA256، وبيئة تصدير الرؤية وملفات wheels وإشعارات التراخيص.

## الاستخدام المحلي

الخدمة الأساسية تبدأ دون انتظار الشبكة أو تحميل النموذج. لتشغيل المحادثة عند الحاجة:

```sh
sudo systemctl start agrirobot-llm
cd /opt/agrirobot
venv/bin/python -m app.assistant status
venv/bin/python -m app.assistant chat 'اشرح حساسات رطوبة التربة باختصار. /no_think'
venv/bin/python -m app.assistant transcribe /path/to/recording.wav
venv/bin/python -m app.assistant speak 'مرحبا' --output /tmp/voice.wav
venv/bin/python -m app.assistant inspect /path/to/photo.jpg
```

ناتج speak ملف WAV؛ تشغيله على مكبر الصوت يتطلب جهاز صوت وتعريفه. النموذج اللغوي منفصل عن التحكم، ولا يتصل بمحركات أو مضخات. API على loopback ومصادق عليه؛ لا يفتح على الإنترنت تلقائيًا.

## حدود الإصدار

الحركة الحقيقية، ربط STM32/ESP32، المعايرة الحقلية، نموذج أمراض النباتات والحشرات المدرب، واجهة رسومية كاملة، وROS ليست مكتملة في هذا الإصدار. معلومات القطع تعتمد على تعريفات موثقة وأدلة قياس؛ الذكاء الاصطناعي لا يمكنه استنتاج جميع التوصيلات الكهربائية من منافذ GPIO. يظل التحكم الفيزيائي معطلًا. نظام Live يحتاج تخزينًا دائمًا لحفظ السجلات بعد إعادة التشغيل.

اختبار QEMU يستخدم 4GiB RAM ومعالجين افتراضيين وTCG دون NIC؛ زمنه ليس وعدًا بسرعة جهاز الروبوت. الإقلاع الفعلي على اللوحة ودقة النماذج في الحقل يحتاجان اختبارات مستقلة.

CPU build profile: x86_64 with SSE4.2, AVX, AVX2, F16C, FMA and BMI2. GGML_NATIVE is disabled but these backend defaults remain enabled; baseline amd64 without these extensions is not supported by this build. Validate target CPU before use.
