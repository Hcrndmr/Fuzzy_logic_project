// Builds presentation.pptx (Turkish). Run: node build_presentation.js  (needs pptxgenjs)
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/a17d32f4-ccd2-496a-958b-1bd9d45b7988_a25db726-894c-4104-81cb-9271bd8b93e8/pptx/scripts/apply_theme.js");
const FIG = "../results/figures/";
const THEME = { name: "TrafficFuzzy", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "1B2631", lt1: "FFFFFF", dk2: "243746", lt2: "EEF2F4", accent1: "2E9E6B", accent2: "E0A526", accent3: "D9534F", accent4: "3C7DA6", accent5: "7F8C8D", accent6: "5B6F82", hlink: "3C7DA6", folHlink: "5B6F82" } };
const pres = new pptxgen(); pres.layout = "LAYOUT_16x9"; pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Interval Type-2 Bulanık Yeşil Süre Kontrolü"; pres.author = "[Ad Soyad]";
const C = pres.SchemeColor;
pres.defineSlideMaster({ title: "TITLE_DARK", background: { color: THEME.colors.dk1 } });
pres.defineSlideMaster({ title: "CONTENT", background: { color: THEME.colors.lt1 },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9, h: 0.8, fontSize: 28, bold: true, color: C.text1, fontFace: THEME.headFontFace, margin: 0, valign: "middle", align: "left" }, text: "" } }],
  slideNumber: { x: 9.2, y: 5.25, w: 0.5, h: 0.3, fontSize: 10, color: C.accent5 } });
const NAVY = "1B2631", GREEN = "2E9E6B", AMBER = "E0A526", RED = "D9534F", BLUE = "3C7DA6", GREY = "7F8C8D";
let n = 0;
function slide(title, notes) { const s = pres.addSlide({ masterName: "CONTENT" }); s.addText(title, { placeholder: "title" }); if (notes) s.addNotes(notes); return s; }
function bullets(s, items, o) { s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 8 } })),
  Object.assign({ x: 0.5, y: 1.3, w: 4.6, h: 3.8, fontSize: 15, color: C.text1, valign: "top", isTextBox: true, margin: 0 }, o)); }
function chartStyle(extra) { return Object.assign({ catAxisLabelColor: "5B6F82", valAxisLabelColor: "5B6F82", catAxisLabelFontSize: 12, valAxisLabelFontSize: 12,
  valGridLine: { color: "DDE3E7", size: 0.5 }, catGridLine: { style: "none" }, showLegend: true, legendPos: "b", legendFontSize: 12, legendColor: "1B2631",
  dataLabelFontSize: 11, dataLabelColor: "1B2631", catAxisLabelFontFace: "Calibri", valAxisLabelFontFace: "Calibri" }, extra); }

// 1 title
let s = pres.addSlide({ masterName: "TITLE_DARK" });
s.addShape(pres.shapes.OVAL, { x: 8.2, y: 0.6, w: 0.5, h: 0.5, fill: { color: RED }, line: { color: RED }, objectName: "red" });
s.addShape(pres.shapes.OVAL, { x: 8.2, y: 1.25, w: 0.5, h: 0.5, fill: { color: AMBER }, line: { color: AMBER }, objectName: "amber" });
s.addShape(pres.shapes.OVAL, { x: 8.2, y: 1.9, w: 0.5, h: 0.5, fill: { color: GREEN }, line: { color: GREEN }, objectName: "green" });
s.addText("Interval Type-2 Bulanık Yeşil Süre Kontrolü", { x: 0.6, y: 1.2, w: 7.2, h: 1.5, fontFace: "Cambria", fontSize: 36, bold: true, color: "FFFFFF", valign: "top", margin: 0, isTextBox: true });
s.addText("Sinyalize bir kavşakta yeniden gerçekleştirme, optimizasyon algoritması karşılaştırması ve dedektör gürültüsüne dayanıklılık", { x: 0.6, y: 2.8, w: 7.2, h: 0.9, fontSize: 16, color: "CADCE4", margin: 0, isTextBox: true });
s.addText("Bulanık Mantık Dersi - Dönem Projesi\n[Ad Soyad] - [Öğrenci No]\nReferans: Korkmaz & Akgüngör, Soft Computing 28:7227-7249, 2024", { x: 0.6, y: 4.2, w: 8, h: 1, fontSize: 13, color: "AEB9C1", margin: 0, isTextBox: true });

// 2 problem
s = slide("Problem: sabit süreli sinyal rastgele varışlara uyum sağlayamaz", "Gerçek dünya problemi: kavşak gecikmesi. Bulanık mantığın nedeni: 'az/çok araç', 'kısa/uzun kuyruk' dilsel ifadeler.");
bullets(s, ["Kavşak gecikmesi: şehir içi seyahat süresinin büyük bölümü", "Sabit süreli plan, ortalama talebe göre kurulur; rastgele dalgalanmaları göremez", "Bulanık mantık: model gerektirmeden 'çok araç + uzun kuyruk → yeşili uzat' gibi kurallar", "Makale: FPA (faz planı) + Type-2 bulanık sistem (CSA ile ayarlı) = HTSC"], { w: 5.3 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.2, y: 1.4, w: 3.3, h: 3.4, fill: { color: THEME.colors.lt2 }, line: { color: THEME.colors.lt2 }, rectRadius: 0.1, objectName: "stat-card" });
s.addText([{ text: "±6 s", options: { fontSize: 48, bold: true, color: GREEN, breakLine: true } }, { text: "sonraki fazın yeşil süresi, iki girişle belirlenir: araç sayısı ve kuyruk uzunluğu", options: { fontSize: 14, color: NAVY } }],
  { x: 6.4, y: 1.7, w: 2.9, h: 2.8, align: "left", valign: "middle", isTextBox: true, margin: 0 });

// 3 literature
s = slide("Literatür: bulanık sinyal kontrolü Type-1'den Type-2'ye", "Tablo makalenin giriş bölümünde özetlenen sonuçlara dayanır; farklı simülatörler olduğu için doğrudan karşılaştırılamaz. Bi 2024, Koukol 2015 ve Agrahari 2024 internette doğrulandı.");
const rows = [["Çalışma", "Yöntem", "Bildirilen etki"],
  ["Trabia vd. 1999", "Type-1, iki aşamalı", "%9,5 daha az gecikme (araç uyarmalıya göre)"],
  ["Doğan & Akgüngör 2016", "Type-1 + DE", "%52 / 48 / 14 (düşük/orta/yüksek)"],
  ["Araghi vd. 2017", "IT2 ANFIS + CS/GA/SA", "%31 / 17 / 3 (sabit süreliye göre)"],
  ["Korkmaz & Akgüngör 2024", "IT2 Sugeno + FPA + CSA", "~%32'ye kadar (sabit süreliye göre)"],
  ["Bi vd. 2024", "Type-2 bulanık + DQN", "DQN'e göre %10,1 gecikme azalması (SUMO)"]];
s.addTable(rows.map((r, i) => r.map(c => ({ text: c, options: { bold: i === 0, color: i === 0 ? "FFFFFF" : NAVY, fill: { color: i === 0 ? NAVY : (i % 2 ? "FFFFFF" : "EEF2F4") }, fontSize: 13, valign: "middle" } }))),
  { x: 0.5, y: 1.35, w: 9, colW: [2.6, 2.7, 3.7], rowH: 0.55, border: { type: "solid", pt: 0.5, color: "DDE3E7" }, fontFace: "Calibri" });
s.addText("Boşluk: Type-2 denetleyiciler tek bir metasezgiselle ayarlanıyor ve çoğunlukla gürültüsüz simülasyonda test ediliyor.", { x: 0.5, y: 4.75, w: 9, h: 0.5, fontSize: 14, italic: true, color: GREY, isTextBox: true, margin: 0 });

// 4 theory
s = slide("Teori: Sugeno çıkarımı ve interval Type-2 küme", "Sugeno: sabit (singleton) sonuçlar. IT2: üst ve alt üyelik fonksiyonu, aradaki bölge FOU. Tip indirgeme: Karnik-Mendel tam uç noktaları bulur; Nie-Tan kapalı formdur.");
bullets(s, ["Üçgen üyelik fonksiyonları (MF), 7 (araç) × 6 (kuyruk) = 42 kural", "Sugeno: y = Σ wᵣ zᵣ / Σ wᵣ, wᵣ = min(μ₁, μ₂)", "IT2: ateşleme aralığı [w̲, w̄]; FOU = üst ve alt MF arası", "Tip indirgeme: Karnik-Mendel (KM) → [y_l, y_r]; çıkış = (y_l + y_r)/2", "Nie-Tan: tek adımda ağırlıklı ortalama (daha ucuz)"], { w: 5.2, fontSize: 14 });
s.addImage({ path: FIG + "mf_4leg_med_equal800.png", x: 5.8, y: 1.5, w: 3.9, h: 2.4, altText: "Üniform ve ayarlanmış IT2 üyelik fonksiyonları" });
s.addText("Üniform ve CSA ile ayarlanmış IT2 MF'ler (çizgi = üst MF, gölge = FOU)", { x: 5.8, y: 4.0, w: 3.9, h: 0.6, fontSize: 11, color: GREY, isTextBox: true, margin: 0 });

// 5 paper method
s = slide("Makalenin yöntemi: FPA ile faz planı, CSA'lı Type-2 ile yeşil süre", "Sistem modülerdir; biz yalnızca yeşil süre modülünü yeniden gerçekleştirdik (MRR).");
s.addImage({ path: FIG + "architecture.png", x: 0.5, y: 1.3, w: 6.0, h: 2.77, altText: "Sistem mimarisi" });
bullets(s, ["Girişler: araç sayısı (0-40), kuyruk uzunluğu (0-175 m)", "Çıkış: yeşil değişimi {-6,…,+6} s", "CSA: MF merkez ve bacaklarını senaryoya göre ayarlar", "KU-Trsim simülatörü, 20 seed, 4 geometri"], { x: 6.7, y: 1.3, w: 2.9, h: 3.4, fontSize: 14 });
s.addText("Yeşil = bu projede yeniden gerçekleştirilen kısım", { x: 0.5, y: 4.3, w: 6, h: 0.4, fontSize: 12, color: GREY, isTextBox: true, margin: 0 });

// 6 critique
s = slide("Eleştirel okuma: makalenin açıkta bıraktığı noktalar", "Bunların hepsi makale metninden doğrulandı: özet %32, Tablo 13 en iyi durum %31,45; sonuç bölümündeki %60 Friedman sıralarından türetilmiş.");
bullets(s, ["Kural tablosu, alt MF yüksekliği, popülasyon boyutu yayımlanmamış", "'~%32' iyileşme = Tablo 13'ün en iyi hücresi; dört geometrinin ortalaması ~%23,5", "'~%60' iyileşme Friedman sıralarından türetilmiş, gecikme yüzdesi değil", "Type-2 üstünlüğü (%2,4-5,7) farklı optimizasyon ve faz optimizasyonuyla karışık", "MF'lerin ayarlandığı seed'ler ile test seed'leri ayrıştırılmış mı belirtilmemiş"], { w: 9, fontSize: 18 });

// 7 repro
s = slide("Yeniden gerçekleştirme: kendi simülatörümüz ve iki bulanık denetleyici", "Simülatör KU-Trsim değildir; olay tabanlı mezoskopik. HCM gecikme modeliyle R2=0,997.");
bullets(s, ["Üstel varışlar, 5 araç tipi, 175 m dedektör, 2 şerit, 900 s", "Faz planı: her bacak ayrı faz; yeşiller FPA + HCM gecikmesiyle", "Tip-1 ve IT2 Sugeno; kural tablosu monoton (kendi tasarımımız)", "CSA: 20 karga × 100 iterasyon, 4 eğitim seed'i; test: 20 ayrı seed", "Doğrulama: simüle gecikme ↔ HCM, R² = 0,997"], { w: 5.4, fontSize: 14 });
s.addImage({ path: FIG + "simulator_vs_hcm.png", x: 6.2, y: 1.4, w: 3.2, h: 3.0, altText: "Simülatör ve HCM karşılaştırması" });

// 8 baseline results
s = slide("Sonuç 1: ayarlı bulanık denetleyiciler gecikmeyi yaklaşık %10 azaltıyor", "Ortalama gecikme (s/araç), 9 senaryo x 20 seed. Type-2'nin Type-1'e üstünlüğü yok (-0,1 ve -0,5 yüzde).");
s.addChart(pres.charts.BAR, [
  { name: "Sabit (Webster)", labels: ["3 kollu", "4 kollu"], values: [36.29, 79.95] },
  { name: "FPA-TSC", labels: ["3 kollu", "4 kollu"], values: [36.25, 78.83] },
  { name: "Type-1 FL", labels: ["3 kollu", "4 kollu"], values: [33.36, 74.85] },
  { name: "IT2 FL", labels: ["3 kollu", "4 kollu"], values: [33.68, 74.87] }],
  Object.assign({ x: 0.4, y: 1.25, w: 5.9, h: 3.9, barDir: "col", chartColors: [GREY, BLUE, AMBER, GREEN], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0",
    showTitle: true, title: "Ortalama gecikme (s/araç)", titleFontSize: 14, titleColor: "1B2631", valAxisMinVal: 0 }, chartStyle({})));
s.addText([{ text: "IT2 - sabit süreli", options: { bold: true, breakLine: true } }, { text: "%10,3 (3 kollu), %10,3 (4 kollu)", options: { breakLine: true } },
  { text: "Makale (HTSC)", options: { bold: true, breakLine: true } }, { text: "%11,6 ve %24,0", options: { breakLine: true } },
  { text: "IT2 - Type-1", options: { bold: true, breakLine: true } }, { text: "-%0,1 ve -%0,5 (makale: +%2,7 ve +%5,3)", options: {} }],
  { x: 6.5, y: 1.5, w: 3.1, h: 3.2, fontSize: 14, color: NAVY, valign: "top", paraSpaceAfter: 6, isTextBox: true, margin: 0 });

// 9 contribution overview
s = slide("Özgün katkı: makalenin ayrıştırmadığı üç soru", "A: optimizasyon algoritması karşılaştırması, B: gürültü, C: tip indirgeme ve maliyet.");
const cards = [["A", "Hangi optimizer?", "CSA, FPA, PSO, DE; eşit bütçe (1220 değerlendirme), 18 senaryo × 3 koşu", GREEN], ["B", "Gürültüde kim dayanıklı?", "σ = %0…75 çarpımsal Gauss gürültüsü; Type-1 ve IT2", AMBER], ["C", "Tip indirgeme ve maliyet", "KM ve Nie-Tan; çıkarım süresi; 100 ve 400 iterasyon", BLUE]];
cards.forEach((c, i) => { const x = 0.5 + i * 3.1;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: 2.9, h: 3.2, fill: { color: THEME.colors.lt2 }, line: { color: THEME.colors.lt2 }, rectRadius: 0.1, objectName: "card" + c[0] });
  s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: 1.75, w: 0.7, h: 0.7, fill: { color: c[3] }, line: { color: c[3] }, objectName: "badge" + c[0] });
  s.addText(c[0], { x: x + 0.25, y: 1.75, w: 0.7, h: 0.7, fontSize: 22, bold: true, color: "FFFFFF", align: "center", valign: "middle", isTextBox: true, margin: 0 });
  s.addText(c[1], { x: x + 0.25, y: 2.6, w: 2.4, h: 0.6, fontSize: 17, bold: true, color: NAVY, valign: "top", isTextBox: true, margin: 0 });
  s.addText(c[2], { x: x + 0.25, y: 3.25, w: 2.4, h: 1.3, fontSize: 14, color: NAVY, valign: "top", isTextBox: true, margin: 0 }); });

// 10 optimizer
s = slide("Deney A: CSA, DE ile aynı düzeyde; FPA ve PSO'dan anlamlı iyi", "Friedman chi2=33,0 p=3e-7; Holm düzeltmeli Wilcoxon: FPA p=0,002, PSO p<0,001, DE p=0,30.");
s.addChart(pres.charts.BAR, [{ name: "Test gecikmesi azalması (%)", labels: ["CSA", "FPA", "PSO", "DE"], values: [12.35, 11.52, 11.23, 12.44] }],
  Object.assign({ x: 0.4, y: 1.25, w: 5.6, h: 3.9, barDir: "col", chartColors: [GREEN, BLUE, AMBER, RED], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", showLegend: false,
    showTitle: true, title: "Üniform MF'e göre test gecikmesi azalması (%)", titleFontSize: 14, titleColor: "1B2631", valAxisMinVal: 0, valAxisMaxVal: 14 }, chartStyle({ showLegend: false })));
bullets(s, ["Ortalama sıra: DE 1,44 · CSA 1,83 · FPA 3,28 · PSO 3,44", "Koşular arası std yalnızca 0,1-0,3 puan", "CSA'nın üstünlüğüne kanıt yok: DE ile ayırt edilemiyor", "Ayarlama süresi her biri için ~21 s"], { x: 6.2, y: 1.4, w: 3.4, h: 3.5, fontSize: 14 });

// 11 noise
s = slide("Deney B: gürültüde IT2 biraz daha az kayıp veriyor, ama anlamlı değil", "H1 doğrulanmadı: yön Type-2 argümanıyla uyumlu, kanıt yok (Wilcoxon p=0,44-1,0).");
const sig = ["0", "10", "20", "30", "50", "75"];
s.addChart(pres.charts.LINE, [{ name: "Type-1 FL", labels: sig, values: [10.35, 9.59, 9.08, 7.74, 5.69, 3.66] }, { name: "IT2 FL", labels: sig, values: [10.17, 9.60, 9.08, 8.02, 6.29, 4.24] }],
  Object.assign({ x: 0.4, y: 1.25, w: 5.9, h: 3.9, chartColors: [AMBER, GREEN], lineSize: 3, lineDataSymbolSize: 8, showValue: false, showTitle: true, title: "Sabit süreliye göre kazanç (%) - gürültü σ (%)", titleFontSize: 14, titleColor: "1B2631", valAxisMinVal: 0 }, chartStyle({})));
bullets(s, ["σ = %75'te bile kazanç pozitif (~%4)", "Gecikme artışı σ = %50: Type-1 %5,4 · IT2 %4,5", "18 senaryoda fark anlamlı değil", "Sonuç: H₁ doğrulanmadı"], { x: 6.5, y: 1.4, w: 3.1, h: 3.5, fontSize: 14 });

// 12 type reduction and cost
s = slide("Deney C: Nie-Tan daha ucuz, +%0,6 gecikme; uzun ayarlama aşırı uyduruyor", "KM 54,28 s, NT 54,62 s, Wilcoxon p=1e-4. 400 iterasyon sekiz durumun altısında test gecikmesini kötüleştirdi.");
const stats = [["14,5 µs", "Type-1 çıkarım"], ["34,7 µs", "IT2 Nie-Tan"], ["51,3 µs", "IT2 Karnik-Mendel"]];
stats.forEach((t, i) => { const x = 0.5 + i * 3.1;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.4, w: 2.9, h: 1.6, fill: { color: THEME.colors.lt2 }, line: { color: THEME.colors.lt2 }, rectRadius: 0.1, objectName: "stat" + i });
  s.addText([{ text: t[0], options: { fontSize: 32, bold: true, color: [BLUE, AMBER, GREEN][i], breakLine: true } }, { text: t[1], options: { fontSize: 14, color: NAVY } }], { x: x + 0.2, y: 1.5, w: 2.5, h: 1.4, valign: "middle", isTextBox: true, margin: 0 }); });
bullets(s, ["KM ile Nie-Tan: 54,28 → 54,62 s (+%0,6, p = 10⁻⁴); NT çıkarımı 1/3 daha ucuz", "100 → 400 iterasyon: eğitim gecikmesi düştü, test gecikmesi sekiz durumun altısında kötüleşti (4 seed'e aşırı uyum)", "IT2 ayarlaması Type-1'den ~3 kat yavaş (65 ve 39 parametre)"], { x: 0.5, y: 3.3, w: 9, h: 1.8, fontSize: 15 });

// 13 limitations
s = slide("Sınırlılıklar ve olası başarısızlık nedenleri", "Dürüst sınırlılıklar. Yüksek talepte 4 kollu senaryolar aşırı doygun.");
bullets(s, ["Mezoskopik simülatör: araç takibi, dönüşler, ivme tabloları yok; mutlak gecikmeler makaleyle kıyaslanamaz", "Her bacak ayrı faz: 4 kollu yüksek talepte doygunluk (X>1); gecikme 111-187 s, makalede ~75-81 s", "FPA faz seçimi, sol dönüş cebi geometrileri ve faz sırası optimizasyonu yeniden gerçekleştirilmedi", "Yayımlanmamış ayrıntılar varsayıldı (kural tablosu, alt MF yüksekliği)", "Yalnızca 4 eğitim seed'i, makaleden 20-33 kat az iterasyon; senaryo bazlı ayarlama"], { w: 9, fontSize: 17 });

// 14 conclusion
s = slide("Sonuç ve gelecek çalışma", "Ana mesaj: yön doğrulandı, Type-2 ek faydası doğrulanmadı.");
bullets(s, ["Ayarlı bulanık denetleyiciler: sabit süreliye göre ~%10 daha az gecikme (makalenin ana iddiası yönce doğrulandı)", "Type-2'nin Type-1'e ek faydası (%2,4-5,7) bizim kurulumumuzda görülmedi", "CSA ≈ DE > FPA, PSO; Nie-Tan ucuz alternatif; gürültüde fark anlamlı değil", "Gelecek: çok yaklaşımlı fazlar ve sol dönüşler, daha çok seed veya dayanıklı amaç, kural tabanı öğrenme"], { w: 9, fontSize: 18 });
s.addText("Üretken YZ kullanımı: kod, metin ve sunum taslağı için Claude kullanıldı; tüm sayılar depodaki kodla üretildi (ayrıntı: raporun 'Generative AI Usage Disclosure' bölümü).", { x: 0.5, y: 4.55, w: 8.6, h: 0.6, fontSize: 12, italic: true, color: GREY, isTextBox: true, margin: 0 });

pres.writeFile({ fileName: "presentation.pptx" }).then(() => applyTheme("presentation.pptx", THEME)).then(() => console.log("ok"));
