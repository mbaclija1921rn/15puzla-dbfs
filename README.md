# 15puzla
Cilj igre je da se kvadrati poređaju od 1 do najvećeg broja po redovima i kolonama pomerajući kvadrate u prazno
polje bez podizanja kvadrata sa stola tako da prazno bolje završi na donjoj desnoj poziciji.
![15puzzle4t4](https://user-images.githubusercontent.com/116192274/206067811-b0688553-05a8-4b18-a1e3-c413b3e3e33c.png)
# Naivno rešenje - BFS
Pretragom svakog stanja broj čvorova u bfs raste eksponenciono ~2 puta u svakoj iteraciji (novi nivo). 
Broj čvorova je (d = dužina rešenja) ~2d. Svaki čvor sadrži kopiju stanja, rešenje od 30 poteza za 
4 puta 4 igru koristi ~16GB memorije. Za 40 poteza ~16TB memorije, itd... Vremenska i memorijska složenost su O(2d).

# Optimizacija: Dvosmerno pretraživanje
Smanjenje grananja korišćenjem dvosmernog pretraživanja (BFS). Početak iz 2 čvora: početni čvor i krajnji čvor. 
Ova dva stabla će da se sretnu na pola puta do suprotnog, posle (d = dužina rešenja) ~2^d/2 čvorova u obe pretrage. To je odprilike  ~2^d/2+1čvorova. 	Nakon svakog poteza proveravamo da li je neki od novih čvorova u suprotnom stablu, broj provera je jednak kao broj čvorova. Ako jeste našli smo presek i rešenje. Ako ne možemo da proširimo neko od stabla, a nismo našli rešenje, rešenje ne postoji.
	
 Širenje stabla jedan nivo može da se izvrši paralelno.
![tree1](https://user-images.githubusercontent.com/116192274/206067790-d3fc8f41-3524-44c4-ba09-31e14891510f.png)
![tree2](https://user-images.githubusercontent.com/116192274/206067792-8a411dc5-693b-48c8-8fa4-f61f1ccb1def.png)

# Rekonstrukcija rešenja
Rekonstruišemo puteve od početnog čvora do preseka i naopaki put od kranjeg čvora do preseka.
	Spajamo puteve tako da se presek ne pojavi 2 puta u rešenju (detaljnije objasnjenje na slici).
	Postoji situacija u kojoj rešenje nije nadjeno.
![intersection](https://user-images.githubusercontent.com/116192274/206067797-2718f94c-d39e-4d3e-9bb8-579e5d67cd53.png)
