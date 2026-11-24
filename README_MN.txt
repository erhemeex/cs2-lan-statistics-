CS2 CAPTAIN DRAFT PRO+ — LAN DEMO STATISTICS + ALL-TIME LEADERBOARD
Windows 10/11 тохируулах заавар

ЮУ ХИЙДЭГ ВЭ?
- CS2-ийн .dem demo файлыг website-ийн Demo Analyzer хэсэгт upload хийнэ.
- Demo доторх тоглогчдыг автоматаар илрүүлнэ. 10 тоглогчоор хязгаарлахгүй: 5v5, 10v10 болон demo-д бүртгэгдсэн бусад тооны тоглогчийг харуулна.
- K/D/A, K/D, HS%, ADR, damage болон тоглолтын мэдээллийг гаргана.
- All-Time Leaderboard дээр бүх хадгалсан тоглолтын статистикийг нэгтгэнэ.
- Ижил нэртэй тоглогчдыг нэг профайлд нэгтгэнэ. Нэр сольсон бол тусдаа бүртгэл болно.
- Ижил demo-г дахин upload хийвэл давхар тоолохгүй.
- Тоглолтын түүхийг matches/history.json файлд хадгална. Хуучин demo устгахгүй бол бүх бүртгэл үлдэнэ.

A. НЭГ КОМПЬЮТЕР ДЭЭР АЖИЛЛУУЛАХ
1. ZIP файлыг татаж ав.
2. ZIP дээр right-click -> Extract All -> Extract.
3. Гарсан хавтсыг нээ.
4. Python 3.11 эсвэл 3.12-г https://www.python.org/downloads/windows/ хаягаас тат.
5. Python суулгахдаа “Add python.exe to PATH” сонголтыг заавал чагтал.
6. Хавтас доторх START_SERVER.bat дээр 2 удаа дар.
7. Эхний удаа шаардлагатай сангууд интернэтээр татагдана. Суулгаж дуусах хүртэл хар цонхыг хааж болохгүй.
8. Browser дээр http://127.0.0.1:8000 нээнэ.
9. CS2 тоглолтын дараа .dem файлаа Demo анализ хэсэгт оруулж DEMO ANALYZE дар.
10. All-Time Leaderboard хэсгээс бүх тоглогчийн нийлбэр үзүүлэлтийг хар.

B. LAN ДЭЭР БУСАД PC-ЭЭС АШИГЛАХ
1. Нэг PC-г website-ийн HOST болго. Тэр PC дээр START_SERVER.bat-ийг ажиллуулж хар цонхыг нээлттэй үлдээнэ.
2. HOST PC дээр Windows + R -> cmd -> Enter.
3. ipconfig гэж бичээд Enter.
4. Ашиглаж буй Ethernet эсвэл Wi-Fi адаптерийн IPv4 Address-ийг ол. Жишээ: 192.168.1.25.
5. Бусад PC-үүд HOST-той ижил LAN/router-д холбогдсон байна.
6. Бусад PC-ийн browser дээр http://192.168.1.25:8000 гэж нээнэ. IP-г HOST PC-ийн бодит IPv4-ээр солино.
7. Windows Firewall асуувал зөвхөн итгэлтэй private LAN-д Python-д Private network access зөвшөөр.
8. Нэг HOST дээр upload хийсэн demo болон leaderboard бүх PC-д ижил харагдана.

C. МЭДЭХ ЗҮЙЛС
- Энэ хувилбар demo upload-аар ажиллана. CS2 серверийн live kill/round мэдээлэл одоогоор шууд дамжихгүй.
- Live статистик хийхийн тулд CS2 серверийн GSI тохиргоо эсвэл серверийн event feed-ийг энэ backend-тэй холбох нэмэлт хөгжүүлэлт шаардлагатай.
- Website-ийн browser дангаараа CS2 demo-г тайлж уншиж чаддаггүй. Demo-г HOST PC дээрх backend боловсруулна.
- Тиймээс website-ийг ажиллуулах HOST PC дээр Python болон шаардлагатай сангууд нэг удаа суусан байх хэрэгтэй. Бусад тоглогчийн PC дээр юу ч суулгах шаардлагагүй, зөвхөн browser ашиглана.
- Demo анализ нь .dem файлд суурилна, MP4 бичлэг биш.
- ADR = player_hurt event-ийн damage / round.
- Score нь community score бөгөөд Valve/CS2-ийн албан ёсны rating биш.
- Тоглогч нэрээ сольвол тусдаа бүртгэл болно.
- HOST-ийн matches/history.json файлыг хадгал. Энэ файлд бүх хуримтлагдсан статистик бий.
- HOST-ийн server цонхыг хаавал website бусад PC-д ажиллахаа болино.


D. ИНТЕРНЭТЭЭР URL-ААР АШИГЛАХ
- DEPLOY_RENDER_MN.txt зааврыг даган GitHub + Render дээр байршуулна.
- Энэ нь Render-ийн төлбөртэй web service болон persistent disk ашигладаг. Төлбөргүй ephemeral hosting дээр all-time history найдвартай хадгалагдахгүй.
- Нийтийн URL дээр нэвтрэх хамгаалалт идэвхтэй; username/password-ийг Render Environment хэсгээс авна.
