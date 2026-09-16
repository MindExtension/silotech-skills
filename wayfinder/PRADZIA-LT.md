# Wayfinder: kaip pradėti

Šis įgūdis skirtas dideliam darbui, kurio pradžioje dar nežinai kelio. Ne kasdienei užduočiai, o tokiam
sumanymui, kuris netelpa į vieną pokalbį. Taip atrodo naujos rinkos įvertinimas, produkto paleidimas,
komandos pertvarka, paraiška finansavimui arba metų strategija.

## Kodėl reikia atskiro įrankio

Vienas pokalbis su DI turi ribotą atmintį. Kai darbas didelis, pokalbis arba nutrūksta viduryje, arba
DI pradeda spėlioti atsakymus į klausimus, kurių dar niekas nesprendė. Wayfinder tą darbą suskaido į
atskirus sprendimus, kiekvieną sprendimą užrašo į atskirą kortelę ir laiko jas viename žemėlapyje. Tada
kiekviena kortelė sprendžiama savo pokalbyje, o žemėlapis lieka tarp pokalbių.

## Keturi žodžiai, kuriuos verta žinoti

**Tikslas.** Kur norime nueiti. Pavyzdžiui: sprendimas, ar einame į Lenkijos rinką. Arba paruoštas
techninis aprašas. Tikslas nustatomas pirmas, nes jis nubrėžia ribas.

**Kortelė.** Vienas klausimas, į kurį reikia atsakyti. Keturi tipai: pokalbis su tavimi, informacijos
paieška, greitas bandomasis pavyzdys ir rankinis darbas (pavyzdžiui, paprašyti pasiūlymo iš tiekėjo).

**Rūkas.** Tai, ką dar matai neaiškiai. Wayfinder sąmoningai nerašo kortelių tam, kas dar per miglota.
Kai išsprendi vieną kortelę, rūkas priekyje prasisklaido ir atsiranda naujų kortelių.

**Pasiekiamos kortelės.** Tos, kurias gali spręsti jau dabar, nes niekas jų nestabdo. Dalis kortelių
laukia kitų sprendimų.

## Kas sprendžia

Kiekviena kortelė turi įrašą, kas ją sprendžia. Numatyta, kad sprendi tu. DI pats gali nuspręsti tik tai,
kas pigu ir lengvai atsukama: pavadinimą, eiliškumą, formatą. Viską, kas kainuoja pinigus, liečia
žmones, įpareigoja įmonę arba eina į viešumą, jis paruošia su rekomendacija ir laukia tavo atsakymo.
Kortelė, kurios tu realiai neatsakei, lieka neišspręsta.

Atskirai kaupiamos **prielaidos**: dalykai, kuriais planas remiasi, bet niekas jų nepatikrino. Prie
kiekvienos parašoma, kas tiksliai žinotų ir kas sugriūtų, jei ji klaidinga. Jei klaidinga prielaida
nuverstų visą tikslą, ji virsta atskira kortele ir tikrinama iš karto.

## Kaip naudoti

Pirmas kartas, kai braižom žemėlapį:

```
/wayfinder norim per metus pradėti pardavinėti Lenkijoje, bet nežinom nuo ko pradėti
```

DI tave išklausinės, užrašys tikslą ir sukurs pirmąsias korteles. Žemėlapis atsiras aplanke
`wayfinder/`, paprastais tekstiniais failais, kuriuos gali skaityti ir be DI.

Toliau kiekvienai kortelei atskiras pokalbis:

```
/wayfinder imk kortelę 03
```

arba tiesiog:

```
/wayfinder
```

ir DI pats paims pirmą laisvą kortelę.

## Ko tikėtis

Vienas pokalbis sprendžia vieną kortelę. Tai nėra lėtumas, tai yra priežastis, kodėl atsakymai lieka
tikslūs. Po kiekvieno pokalbio žemėlapyje atsiranda vienos eilutės įrašas, ką nusprendėm, ir nuoroda į
pilną pokalbio rezultatą.

Kai kortelių nebelieka, žemėlapis virsta tuo, ko prašė tikslas: planu, aprašu arba sprendimu. Kiekvienas
jo teiginys turi nuorodą į kortelę, kurioje tas dalykas buvo nuspręstas, tai visada matai, iš kur
atsakymas atsirado.

## Kada nenaudoti

Jei kelią jau žinai, wayfinder tik trukdys. Jis atsiperka tik tada, kai iš tikrųjų nežinai, kokie yra
žingsniai, ir reikia pradėti judėti, kad tai paaiškėtų.
