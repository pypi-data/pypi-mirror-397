import os
import sys
from querycraft.LLM import *
from querycraft.tools import existFile,diff_dates_iso,loadCache,saveCache,clear_line

class SQLException(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message

    def __unicode__(self):
        return self.message

class SQLQueryException(SQLException):
    model = "gemma3:1b"
    service = "ollama"
    api_key = None
    url = None
    ia_on = False
    duree = 2

    #cache = dict()
    cache_file = ""

    @classmethod
    def set_model(cls, service, model, api_key=None, url=None, ia_on=True, duree = 2):
        cls.model = model
        cls.api_key = api_key
        cls.service = service
        cls.url = url
        cls.ia_on = ia_on
        cls.cache_file = "error_"+(cls.service+"_"+cls.model).replace(':','_').replace('/','_')+'.json'
        cls.duree = duree

    @classmethod
    def get_model(cls):
        return cls.model


    def __init__(self,verbose, message, sqlhs, sqlok, sgbd, bd = ""):
        super().__init__(message)
        self.sqlhs = sqlhs
        if sqlok is None : self.sqlok = ""
        else: self.sqlok = sqlok
        self.sgbd = sgbd
        self.hints = ""
        print(
            f"{RED}Erreur sur la requête SQL avec {self.sgbd} :\n -> Requête proposée : {self.sqlhs}\n -> Message {self.sgbd} :\n{self.message}{RESET}")  # Affichage de l'erreur de base
        if verbose and SQLQueryException.ia_on :
            #print(f"{SQLQueryException.model},{SQLQueryException.api_key}, {SQLQueryException.url}")
            #input("Appuyez sur Entrée pour avoir une explication de l'erreur par IA ou Ctrl + Z pour quitter.")
            #clear_line()
            print("Construction de l'explication. Veuillez patienter.")
            maintenant = datetime.now().date().isoformat()
            cache = loadCache(SQLQueryException.cache_file, SQLQueryException.duree)

            if self.sqlhs+self.sqlok in cache:
                (self.hints, date) = cache[self.sqlhs + self.sqlok]
                self.hints += f"{BLUE} (cache){RESET}"
            else :
                if SQLQueryException.service == "ollama" :
                    #print("Appel ollama")
                    self.hints = OllamaLLM(verbose,self.sgbd,SQLQueryException.get_model(),
                                           bd).run(str(self.message), self.sqlok, self.sqlhs)
                    saveCache(SQLQueryException.cache_file, cache, self.sqlhs + self.sqlok, self.hints)
                elif SQLQueryException.service == "poe" :
                    #print("Appel POE")
                    self.hints = PoeLLM(verbose, self.sgbd, modele=SQLQueryException.model,
                                        api_key=SQLQueryException.api_key, base_url='https://api.poe.com/v1',#SQLQueryException.url,
                                        bd=bd).run(str(self.message), self.sqlok, self.sqlhs)
                    saveCache(SQLQueryException.cache_file, cache, self.sqlhs + self.sqlok, self.hints)
                elif SQLQueryException.service == "openai":
                    # print("Appel Open AI")
                    self.hints = OpenaiLLM(verbose, self.sgbd, modele=SQLQueryException.model,
                                        api_key=SQLQueryException.api_key, base_url='https://api.openai.com/v1/chat/completions',#SQLQueryException.url,
                                        bd=bd).run(str(self.message), self.sqlok, self.sqlhs)
                    saveCache(SQLQueryException.cache_file, cache, self.sqlhs + self.sqlok, self.hints)
                elif SQLQueryException.service == "google":
                    # print("Appel Google Gemini")
                    self.hints = GoogleLLM(verbose, self.sgbd, modele=SQLQueryException.model,
                                           api_key=SQLQueryException.api_key, base_url='https://generativelanguage.googleapis.com/v1beta/openai/',#SQLQueryException.url,
                                           bd=bd).run(str(self.message), self.sqlok, self.sqlhs)
                    saveCache(SQLQueryException.cache_file, cache, self.sqlhs + self.sqlok, self.hints)
                elif SQLQueryException.service == "generic":
                    # print("Appel API Générique")
                    self.hints = GenericLLM(verbose, self.sgbd, modele=SQLQueryException.model,
                                           api_key=SQLQueryException.api_key,
                                           base_url=SQLQueryException.url,
                                           bd=bd).run(str(self.message), self.sqlok, self.sqlhs)
                    saveCache(SQLQueryException.cache_file, cache, self.sqlhs + self.sqlok, self.hints)
                elif SQLQueryException.service == "huggingchat":
                    # print("Appel API HuggingChat")
                    self.hints = HuggingLLM(verbose, self.sgbd, modele=SQLQueryException.model,
                                            #api_key=SQLQueryException.api_key,
                                            base_url='https://router.huggingface.co/v1',
                                            bd=bd).run(str(self.message), self.sqlok, self.sqlhs)
                    saveCache(SQLQueryException.cache_file, cache, self.sqlhs + self.sqlok, self.hints)
                else :
                    self.hints = ""

                clear_line()
                if not self.hints:
                    print("Modèle pas accessible, utilisation du modèle par défaut")
                    cache = loadCache("error_default.json", SQLQueryException.duree)
                    if self.sqlhs + self.sqlok in cache:
                        (self.hints, date) = cache[self.sqlhs+ self.sqlok]
                        self.hints += f"{BLUE} (cache){RESET}"
                    else :
                        # gpt-4.1-nano ; gpt-5-nano ; gpt-5.1-codex
                        #print("Appel POE 2")
                        self.hints = PoeLLM(verbose,self.sgbd,
                                        "gpt-5-nano", "umnm9e2VrXsAX6FDurYa8ThkRTcYSHuQMzb22xjnh0A","https://api.poe.com/v1",
                                        bd).run(str(self.message), self.sqlok, self.sqlhs)
                        saveCache("error_default.json", cache, self.sqlhs + self.sqlok, self.hints)
                    clear_line()

    def __str__(self):
        #mssg = f"{RED}Erreur sur la requête SQL avec {self.sgbd} :\n -> Requête proposée : {self.sqlhs}\n -> Message {self.sgbd} :\n{self.message}{RESET}"
        mssg = ""
        if self.hints != "":
            mssg += f"\n{GREEN} -> Aide :{RESET} {self.hints}"
        return mssg

    def __repr__(self):
        return self.__str__()
    def __unicode__(self):
        return self.__str__()
