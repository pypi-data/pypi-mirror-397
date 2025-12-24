# https://github.com/ollama/ollama-python
import importlib.resources
from datetime import datetime
from typing import List, Dict, Any

import openai

# https://github.com/Soulter/hugging-chat-api
from hugchat import hugchat
from hugchat.login import Login

from ollama import chat, ChatResponse

from querycraft.tools import getPrompt

# Définir les codes de couleur
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

class LLM():
    def __init__(self, verbose, sgbd, modele, bd=None):
        self.prompt = str()
        self.modele = modele
        self.bd = bd
        self.sgbd = sgbd
        self.prompt_systeme = self.__build_prompt_contexte(sgbd, bd)
        self.verbose = verbose

    def __build_prompt_contexte(self, sgbd, bd=None):
        prompt = getPrompt("systeme_prompt.md")
        return prompt.replace("{{sgbd}}", sgbd).replace("{{database_schema}}", f"{bd}")

    def set_prompt_err(self, erreur, sql_soumis):
        prompt = getPrompt("erreur_prompt.md")
        self.prompt =  prompt.replace("{{erreur}}", erreur).replace("{{requete_err}}", f"{sql_soumis}")

    def set_prompt_err2(self, erreur, sql_attendu, sql_soumis):
        prompt = getPrompt("erreur2_prompt.md")
        self.prompt =  prompt.replace("{{erreur}}", erreur).replace("{{requete_err}}", f"{sql_soumis}").replace("{{requete}}", f"{sql_attendu}")

    def set_prompt_req(self, sql_soumis):
        prompt = getPrompt("requete_prompt.md")
        self.prompt =  prompt.replace("{{requete}}", f"{sql_soumis}")

    def set_prompt_db(self):
        self.prompt = getPrompt("database_prompt.md")

    def run(self, erreur, sql_attendu, sql_soumis):
        return ""

    def set_reponse(self, rep, llm, link, modele, date):
        return (f"{GREEN} {rep} {RESET}\n---\n"
                + f"{BLUE}Source : {llm} ({link}) avec {modele} {RESET}"
                + f"{BLUE} le {date.date()} à {date.time()}. {RESET}\n"
                + f"{BLUE}Attention, {llm}/{modele} ne garantit pas la validité de l'aide. "
                + f"Veuillez vérifier la réponse et vous rapprocher de vos enseignants si nécessaire.{RESET}\n"
                )

class OllamaLLM(LLM):
    def __init__(self, verbose, sgbd, modele="gemma3:1b", bd=None):
        super().__init__(verbose, sgbd, modele, bd)

    def run(self, erreur, sql_attendu, sql_soumis):
        try:
            if erreur is not None and sql_attendu is None :
                #print("Erreur")
                self.set_prompt_err(erreur, sql_soumis)
            elif erreur is not None and sql_attendu is not None :
                #print("Erreur2")
                self.set_prompt_err2(erreur, sql_attendu, sql_soumis)
            elif sql_soumis is None and sql_attendu is not None:
                #print("Requête")
                self.set_prompt_req(sql_attendu)
            else:
                #print("Database")
                self.set_prompt_db()
            response: ChatResponse = chat(model=self.modele, options={"temperature": 0.0, "top-p": 0.9}, messages=[
                {'role': 'system', 'content': self.prompt_systeme},
                {'role': 'user', 'content': self.prompt},
            ])
            if False: #self.verbose:
                print(f"{CYAN}================================{RESET}")
                print(f"{CYAN}================================{RESET}")
                print(f"{CYAN}================================{RESET}")
                print(f"{CYAN}{self.prompt_systeme}{RESET}")
                print(f"{CYAN}================================{RESET}")
                print(f"{CYAN}{self.prompt}{RESET}")
                print(f"{CYAN}================================{RESET}")
                print(f"{CYAN}================================{RESET}")
                print(f"{CYAN}================================{RESET}")
            return self.set_reponse(response.message.content, "Ollama", "https://ollama.com/",
                                    self.modele, datetime.now())
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)

class GenericLLM(LLM):
    def __init__(self, verbose, sgbd, modele, api_key, base_url, bd=None):
        super().__init__(verbose, sgbd, modele, bd)
        self.api_key = api_key
        self.base_url= base_url
        self.client = openai.OpenAI(api_key=self.api_key,base_url=self.base_url,)

    def run(self, erreur, sql_attendu, sql_soumis):
        try:
            response = self.query(erreur, sql_attendu, sql_soumis)
            return self.set_reponse(response.choices[0].message.content, "Generic LLM", "API Reference - OpenAI",
                                    self.modele, datetime.now())
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)

    def query(self, erreur, sql_attendu, sql_soumis):
        try:
            if erreur is not None and sql_attendu is None :
                #print("Erreur")
                self.set_prompt_err(erreur, sql_soumis)
            elif erreur is not None and sql_attendu is not None :
                self.set_prompt_err2(erreur, sql_attendu, sql_soumis)
            elif sql_soumis is None and sql_attendu is not None:
                self.set_prompt_req(sql_attendu)
            else: self.set_prompt_db()
            response = self.client.chat.completions.create(model=self.modele, temperature= 0.0, messages=[
                {'role': 'system', 'content': self.prompt_systeme},
                {'role': 'user', 'content': self.prompt},
            ])
            return response
        except Exception as e:
            print(e)
            return ""


class PoeLLM(GenericLLM):
    def __init__(self, verbose, sgbd, modele, api_key, base_url = 'https://api.poe.com/v1', bd=None):
        super().__init__(verbose, sgbd, modele,api_key, 'https://api.poe.com/v1', bd)

    def run(self, erreur, sql_attendu, sql_soumis):
        try:
            response = self.query(erreur, sql_attendu, sql_soumis)
            return self.set_reponse(response.choices[0].message.content, "POE", "https://poe.com/",
                                    self.modele, datetime.now())
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)

class GoogleLLM(GenericLLM):
    def __init__(self, verbose, sgbd, modele, api_key, base_url = 'https://generativelanguage.googleapis.com/v1beta/openai/', bd=None):
        super().__init__(verbose, sgbd, modele, bd)
        self.api_key = api_key
        self.base_url= base_url
        self.client = openai.OpenAI(api_key=self.api_key)

    def run(self, erreur, sql_attendu, sql_soumis):
        try:
            response = self.query(erreur, sql_attendu, sql_soumis)
            return self.set_reponse(response.choices[0].message.content,
                                    "Google", "https://ai.google.dev/gemini-api/",
                                    self.modele, datetime.now())
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)

class OpenaiLLM(GenericLLM):
    def __init__(self, verbose, sgbd, modele, api_key, base_url = 'https://api.openai.com/v1/chat/completions', bd=None):
        super().__init__(verbose, sgbd, modele, bd)
        self.api_key = api_key
        self.base_url= base_url
        self.client = openai.OpenAI(api_key=self.api_key)

    def run(self, erreur, sql_attendu, sql_soumis):
        try:
            response = self.query(erreur, sql_attendu, sql_soumis)
            return self.set_reponse(response.choices[0].message.content, "Open AI", "https://openai.com/",
                                    self.modele, datetime.now())
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)


class HuggingLLM(LLM):
    def __init__(self, verbose, sgbd, modele, base_url = 'https://router.huggingface.co/v1', bd=None):
        super().__init__(verbose, sgbd, modele, bd)
        self.base_url= base_url

    def run(self, erreur, sql_attendu, sql_soumis):
        try:
            EMAIL = "emmanuel.desmontils@univ-nantes.fr"
            PASSWD = ""
            with importlib.resources.files("querycraft.cookies").joinpath('') as cookie_path_dir:
                cpd = str(cookie_path_dir) + '/'
                print(cpd)
                # cookie_path_dir = "./cookies/"  # NOTE: trailing slash (/) is required to avoid errors
                sign = Login(EMAIL, PASSWD)
                cookies = sign.login(cookie_dir_path=cpd, save_cookies=True)

                chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

                # Create a new conversation with an assistant
                ASSISTANT_ID = self.modele  # get the assistant id from https://huggingface.co/chat/assistants
                chatbot.new_conversation(assistant=ASSISTANT_ID, switch_to=True)

                if erreur is not None:
                    self.set_prompt_err(erreur, sql_attendu, sql_soumis)
                if sql_soumis is None and sql_attendu is not None:
                    self.set_prompt_req(sql_attendu)
                else:
                    self.set_prompt_db()

                if self.verbose:
                    print(f"{CYAN}{self.prompt_systeme}\n\n{self.prompt}{RESET}")
                return (f"{GREEN}" + chatbot.chat(self.prompt).wait_until_done() + f"{RESET}\n---\n"
                        + f"{BLUE}Source : HuggingChat (https://huggingface.co/chat/), assistant Mia-DB (https://hf.co/chat/assistant/{self.modele}) {RESET}\n"
                        + f"{BLUE}Attention, HuggingChat/Mia-DB ne garantit pas la validité de l'aide. Veuillez vérifier la réponse et vous rapprocher de vos enseignants si nécessaire.{RESET}")
                #return self.set_reponse(chatbot.chat(self.prompt).wait_until_done(), "HuggingChat", "https://huggingface.co/chat/", self.modele,
                #                        datetime.now())
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)  # + f"\nPb HuggingChat : {e}"


def main():
    pass
    # swiss-ai/Apertus-70B-Instruct-2509
    # mess = HuggingLLM(True, "PostgreSQL", "67bc5132aea628b3325f2f8b", BdD).run(erreur2, sql2, sql2e)
    #print(mess)


if __name__ == '__main__':
    main()
