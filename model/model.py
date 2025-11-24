from copy import deepcopy

from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        # TODO
        relazioni= TourDAO.get_tour_attrazioni()
        for row in relazioni:
            id_tour= row["id_tour"]
            id_attrazione= row["id_attrazione"]
            tour= self.tour_map[id_tour]
            attrazione= self.attrazioni_map[id_attrazione]
            tour.attrazioni.add(attrazione)
            attrazione.tour.add(tour)



    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        tour_regione=[]
        for tour in self.tour_map.values():
            if tour.id_regione == id_regione:
                tour_regione.append(tour)
        self._tour_regione=tour_regione
        self._max_giorni=max_giorni
        self._max_budget=max_budget
        self._ricorsione(
            start_index = 0,
        pacchetto_parziale = [],
        durata_corrente = 0,
        costo_corrente = 0.0,
        valore_corrente = 0,
        attrazioni_usate = set()
        )

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._costo = costo_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()
        for i in range(start_index, len(self._tour_regione)):
            tour= self._tour_regione[i]
            nuova_durata= durata_corrente + tour.durata_giorni
            nuovo_costo= costo_corrente + tour.costo
            if  self._max_giorni is not None and nuova_durata > self._max_giorni :
                continue
            if self._max_budget is not None and nuovo_costo > self._max_budget :
                continue
            attrazioni_in_comune= attrazioni_usate.intersection(tour.attrazioni)
            if attrazioni_in_comune:
                continue
            attrazioni_nuove= tour.attrazioni.difference(attrazioni_usate)
            incremento_valore=0
            for attr in attrazioni_nuove:
                incremento_valore += attr.valore_culturale
            nuovo_valore= valore_corrente + incremento_valore
            pacchetto_parziale.append(tour)
            attrazioni_usate.update(attrazioni_nuove)
            self._ricorsione(
                start_index=i+1,
                pacchetto_parziale=pacchetto_parziale,
                durata_corrente=nuova_durata,
                costo_corrente=nuovo_costo,
                valore_corrente=nuovo_valore,
                attrazioni_usate=attrazioni_usate
            )
            pacchetto_parziale.pop()
            attrazioni_usate.difference_update(attrazioni_nuove)