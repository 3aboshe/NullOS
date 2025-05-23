# nullx_dialogue_ar.py

# Arabic translations for NullX dialogue
NULLX_DIALOGUE = {
    1: [ # Level 1: EXIF / Metadata
        {'image': 'NullX_explaining.png',
         'text': "مرحبًا أيها الوكيل! نولكس هنا. مستعد للغوص في التحقيق الجنائي الرقمي؟ مهمتك الأولى تتعلق بـ 'البيانات الوصفية' - البيانات *حول* البيانات."},
        {'image': 'NullX_speaking.png',
         'text': "فكر فيها مثل الملصق على ملف مجلد. تحتوي ملفات الصور على بيانات EXIF: طراز الكاميرا، تاريخ الالتقاط، إحداثيات GPS... أشياء مثيرة!"},
        {'image': 'NullX_explaining.png',
         'text': "لماذا تهتم؟ لأن هذه البيانات الوصفية تحتوي أحيانًا على أدلة مخفية أو تعليقات مدمجة مباشرة من قبل شخص ما... ربما هدفنا؟"},
        {'image': 'NullX_speaking.png',
         'text': "قصة حقيقية: كان جون ماكافي يختبئ. نشر صحفي صورة له على الإنترنت. خطأ! لا تزال بيانات EXIF للصورة تحتوي على إحداثيات GPS، مما كشف عن موقعه للعالم!"},
        {'image': 'NullX_speaking.png',
         'text': "البيانات الوصفية مهمة! استخدم الأمر 'exif' على ملف الصورة ذلك. ابحث عن العلم المخفي. انقر على المطالبة أدناه عندما تكون مستعدًا للمتابعة!"},
    ],
    2: [ # Level 2: Strings / File Analysis
        {'image': 'NullX_explaining.png',
         'text': "عمل رائع في إيجاد البيانات الوصفية! الآن، دعنا نلقي نظرة *داخل* الملفات، تحديداً البرامج التنفيذية."},
        {'image': 'NullX_explaining.png',
         'text': "البرامج تتكون في الغالب من كود الآلة، لكنها غالباً تحتوي على أجزاء نصية قابلة للقراءة تُعرف بـ 'Strings'. ممكن تكون رسائل خطأ، مسارات ملفات، روابط، أو حتى أسرار نُسيت داخلها!"},
        {'image': 'NullX_speaking.png',
         'text': "أمر 'strings' يقوم بمسح الملف بحثاً عن تسلسلات من الأحرف القابلة للقراءة. كأنه يصطاد نصوص واضحة وسط بحر من البيانات الثنائية."},
        {'image': 'NullX_speaking.png',
         'text': "في العالم الحقيقي؟ محللو البرمجيات الخبيثة يستخدمونه دائماً! يكتشفون من خلاله عناوين خوادم التحكم، رسائل خفية من مطور البرمجية، أو دلائل على وظيفة البرنامج."},
        {'image': 'NullX_Cheering.png',
         'text': "شغل أمر 'strings' على الملف المشبوه. شوف شنو النصوص اللي راح تكتشفها! جاهز؟ اضغط بالأسفل!"},
    ],
   3: [ # Level 3: Base64 Decoding
        {'image': 'NullX_explaining.png',
         'text': "أنت تتحسن بالفعل! أحياناً، لا تكون البيانات مخفية، بل مُموّهة. هل سبق أن رأيت نصاً طويلاً مليئاً بالحروف والأرقام، وربما رمزي '+' و'/'؟"},
        {'image': 'NullX_explaining.png',
         'text': "قد يكون هذا ترميز Base64! فهو يحوّل البيانات الثنائية إلى نصوص قابلة للإرسال. ليس تشفيراً، بل وسيلة شائعة لتمثيل البيانات كنص عادي. غالباً ما ينتهي بعلامة '='."},
        {'image': 'NullX_speaking.png',
         'text': "الهجمات الاحتيالية تعتمد كثيراً على Base64! تُشفَّر الروابط الضارة أو أوامر البرمجة النصية. مرشح النصوص قد يتجاهل 'aHR0cHM6Ly9ldmlsLnNpdGU='، لكن فك الترميز يكشف 'https://evil.site'!"},
        {'image': 'NullX_speaking.png',
         'text': "فكّر به كرمز تحويل، لا كرمز سري. نحتاج فقط إلى الأداة المناسبة لعكسه."},
        {'image': 'NullX_speaking.png',
         'text': "افتح ملف السجل. هل ترى سلاسل تشبه Base64؟ استخدم الأمر 'decode64'! هيا نحلها. اضغط عندما تكون جاهزاً!"},
    ],
    4: [ # Level 4: Steganography (Simple File Embedding/Appending)
        {'image': 'NullX_explaining.png',
         'text': "عدنا إلى الصور! لكن هذه المرة، السر ليس في البيانات الوصفية فقط. نحن نبحث عن إخفاء البيانات داخل الملف نفسه."},
        {'image': 'NullX_explaining.png',
         'text': "بعض الطرق معقّدة، لكن الطريقة البسيطة هي إضافة بيانات جديدة بعد نهاية بيانات الصورة الأصلية."},
        {'image': 'NullX_speaking.png',
         'text': "برامج عرض الصور تتجاهل عادةً أي بيانات بعد علامة نهاية الصورة. لذا يمكن إلحاق نص أو ملف آخر أو أي شيء. سيبقى مخفياً ما لم يبحث أحد خلف النهاية."},
        {'image': 'NullX_speaking.png',
         'text': "أدوات التحليل الجنائي، أو بعض أوامر 'extract'، يمكنها فحص البيانات المضافة بعد البنية المعروفة للملف. هذا النوع أقل استخداماً في البرمجيات الخبيثة، وأكثر شيوعاً في التحديات أو إخفاء الملاحظات."},
        {'image': 'NullX_speaking.png',
         'text': "تلك الصورة... قد تحتوي على ما هو أكثر مما يبدو. جرّب أمر 'extract'. انظر إن كان هناك شيء إضافي! هل أنت مستعد؟ اضغط أدناه!"},
    ],
    5: [ # Level 5: Zip Passwords / Git History
        {'image': 'NullX_explaining.png',
         'text': "التحدي الأخير، أيها العميل! مكون من جزأين: الأرشيفات المشفّرة وتاريخ التعديلات البرمجية."},
        {'image': 'NullX_explaining.png',
         'text': "ملفات ZIP يمكن حمايتها بكلمة مرور. أحياناً، يترك البعض تلميحات داخل تعليق الملف نفسه! استخدم الأمر 'exif' على الملف المضغوط."},
        {'image': 'NullX_speaking.png',
         'text': "ولدينا Git - أداة يستخدمها المطورون لتتبع تغييرات الشيفرة. كل عملية حفظ تُسجّل. إذا تم حفظ كلمة مرور ثم حذفها... ستبقى ظاهرة في سجل 'git log'."},
        {'image': 'NullX_Wondering.png',
         'text': "هذا يحدث فعلاً! وقعت تسريبات ضخمة لأن مطورين نسوا إزالة مفاتيح API أو بيانات حساسة من تاريخ Git بعد نشرها."},
        {'image': 'NullX_Cheering.png',
         'text': "أولاً، افحص بيانات ZIP باستخدام 'exif' للبحث عن تلميحات كلمة المرور. ثم استخدم 'unzip'. بعد الدخول، تحقق من ملف الملاحظات. هل له تاريخ؟ استخدم 'git log'. انطلق! اضغط أدناه!"},
    ],

}