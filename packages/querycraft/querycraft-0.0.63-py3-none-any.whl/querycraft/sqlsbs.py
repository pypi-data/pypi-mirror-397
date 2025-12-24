#!/usr/bin/env python3

import argparse
import importlib.resources
import os
import sys
from configparser import ConfigParser

from querycraft.Database import *
from querycraft.LLM import *
from querycraft.LRS import LRS
from querycraft.SQL import SQL
from querycraft.tools import loadCache, saveCache, diff_dates_iso, readConfigFile,clear_line, existFile

# Définir les codes de couleur
RESET = "\033[0m"
GREEN = "\033[32m"
BOLD = "\033[1m"
BLUE = "\033[34m"

def sbs(sql, cfg, verbose=False):
    if verbose:
        print(f"Bonjour {os.getlogin()} !")
        print('==================================================================================================')
        print('======================================== Requête à analyser ======================================')
        print('==================================================================================================\n')
        print("--- Schéma de la base ---")
        sql.printDBTables()
        print('--- Requête à exécuter ---')
        print(sql)
        print('\n--- Table à obtenir ---')
        # print(sql.getPLTable())
        (hd, rows) = sql.getTable()
        print(format_table_2(hd, rows))

        if cfg['IA']['mode'] == 'on':
            print("Construction de l'explication. Veuillez patienter.")
            duree = int(cfg['IA']['duree-cache'])
            cache_file = "explain_" + (cfg['IA']['service'] + "_" + cfg['IA']['modele']).replace(':', '_') + ".json"
            maintenant = datetime.now().date().isoformat()
            cache = loadCache(cache_file, duree)
            str_sql = f"{sql}"
            if str_sql in cache:
                (rep, dt) = cache[str_sql]
                rep += f"{BLUE}(cache){RESET}"
            else:
                rep = ""
            if rep == "":
                if cfg['IA']['service'] == 'ollama':
                    rep = OllamaLLM(verbose, cfg['Database']['type'], cfg['IA']['modele'],
                                    sql.getDB().tables2string()).run(None, sql, None)
                elif cfg['IA']['service'] == 'poe':
                    rep = PoeLLM(verbose, cfg['Database']['type'], cfg['IA']['modele'], api_key=cfg['IA']['api-key'],
                                 base_url='https://api.poe.com/v1',
                                 bd=sql.getDB().tables2string()).run(None, sql, None)
                elif cfg['IA']['service'] == 'openai':
                    rep = OpenaiLLM(verbose, cfg['Database']['type'], cfg['IA']['modele'], api_key=cfg['IA']['api-key'],
                                    base_url='https://api.openai.com/v1/chat/completions',
                                    bd=sql.getDB().tables2string()).run(None, sql, None)
                elif cfg['IA']['service'] == 'google':
                    rep = GoogleLLM(verbose, cfg['Database']['type'], cfg['IA']['modele'], api_key=cfg['IA']['api-key'],
                                    base_url='https://generativelanguage.googleapis.com/v1beta/openai/',
                                    bd=sql.getDB().tables2string()).run(None, sql, None)
                elif cfg['IA']['service'] == 'generic':
                    rep = GenericLLM(verbose, cfg['Database']['type'], cfg['IA']['modele'],
                                     api_key=cfg['IA']['api-key'],
                                     base_url=cfg['IA']['url'],
                                     bd=sql.getDB().tables2string()).run(None, sql, None)
                else:
                    rep = ""
                saveCache(cache_file, cache, str_sql, rep)
            if not rep:
                cache = loadCache("explain_default.json", duree)
                if str_sql in cache:
                    (rep, date) = cache[str_sql]
                    rep += f"{BLUE}(cache){RESET}"

                if rep == "":
                    # gpt-4.1-nano ; gpt-5-nano ; gpt-5.1-codex
                    # print("Appel POE 2")
                    rep = PoeLLM(verbose, cfg['Database']['type'],
                                 "gpt-5-nano", "umnm9e2VrXsAX6FDurYa8ThkRTcYSHuQMzb22xjnh0A",
                                 "https://api.poe.com/v1",
                                 sql.getDB().tables2string()).run(None, sql, None)
                    saveCache("explain_default.json", cache, str_sql, rep)
            clear_line()
            if rep:
                print(f"\n{BLUE}--- Explication de la requête par IA générative ---{RESET}")
                print(rep)

        print('==================================================================================================')
        print('========================================== Pas à pas =============================================')
        print('==================================================================================================\n')
    sql.sbs()
    if verbose: print('fin')


def getQuery(args):
    if args.file and existFile(args.file):
        sqlTXT = ''
        with open(args.file, 'r') as f:
            sqlTXT += f.read()
    elif args.sql:
        sqlTXT = args.sql
    else:
        sqlTXT = ''
    return sqlTXT


def stdArgs(parser, def_db):
    if def_db:
        parser.add_argument('-d', '--db', help=f'database name (by default {def_db})', default=def_db)
    else:
        parser.add_argument('-d', '--db', help=f'database name', required=True)

    parser.add_argument('-v', '--verbose', help='verbose mode', action='store_true', default=False)
    parser.add_argument('-nsbs', '--step_by_step', help='step by step mode off', action='store_false', default=True)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', '--describe', help='DB Schema', action='store_true', default=False)
    group.add_argument('-f', '--file', help='sql file')
    group.add_argument('-s', '--sql', type=str, help='sql string')

    return parser


def dbConnectArgs(parser, defaultPort, defaultHost='localhost', defaultUser='desmontils-e'):
    parser.add_argument('-u', '--user', help=f'database user (by default {defaultUser})',
                        default=defaultUser)  # 'desmontils-e')
    parser.add_argument('-p', '--password', help='database password', default=None)
    parser.add_argument('--host', help=f'database host (by default {defaultHost})', default=defaultHost)  # 'localhost')
    parser.add_argument('--port', help=f'database port (by default {defaultPort})', default=defaultPort)  # '5432')


def doSBS(db, dbtype, dbname, sqlTXT, debug, verbose, step_by_step, lrs=None):
    # clear_terminal()
    try:
        cfg = readConfigFile()

        # IA configuration
        model = cfg['IA']['modele']
        if debug: print('Modele : ', model)
        SQLQueryException.set_model(cfg['IA']['service'], model, cfg['IA']['api-key'], cfg['IA']['url'],
                                    cfg['IA']['mode'], int(cfg['IA']['duree-cache']))

        # LRS configuration
        if lrs:
            lrs.setContextSBS()
        sql = SQL(db=db, dbtype=dbtype, debug=debug, verbose=verbose, step_by_step=step_by_step)
        sql.setSQL(sqlTXT)
        if lrs: lrs.sendSBSExecute(dbtype, dbname, sqlTXT)

        # Lancement du programme
        try:
            sbs(sql, cfg, verbose)  # Pas à pas
            if lrs: lrs.sendSBSpap(dbtype, dbname, sqlTXT)
        except Exception as e:
            # LRS : envoie du statement
            if lrs: lrs.sendSBSpap(dbtype, dbname, sqlTXT, error=e)
            print(f'Erreur SBS : {e}')
    except Exception as e:
        print(f"{e}")
        # LRS : envoie du statement
        if lrs: lrs.sendSBSExecute(dbtype, dbname, sqlTXT, error=e)
        exit()


def getDesc(cfg, str_sql, cacheName, verbose=False):
    pass


def doDescribe(cfg, sgbd, verbose=False):
    if verbose and (cfg['IA']['mode'] == 'on'):
        # print(f"Description de la base de données {sgbd.dbname} ({sgbd.dbtype})")
        duree = int(cfg['IA']['duree-cache'])
        print("Construction de l'explication. Veuillez patienter.")
        cache_file = "describe_" + (cfg['IA']['service'] + "_" + cfg['IA']['modele']).replace(':', '_') + ".json"
        maintenant = datetime.now().date().isoformat()
        cache = loadCache(cache_file, duree)
        str_sql = f"{sgbd.dbtype}-{sgbd.db}"
        if str_sql in cache:
            (rep, dt) = cache[str_sql]
            rep += f"{BLUE}(cache){RESET}"
        else:
            if cfg['IA']['service'] == 'ollama':
                rep = OllamaLLM(verbose, cfg['Database']['type'], cfg['IA']['modele'],
                                sgbd.tables2string()).run(None, None, None)
            elif cfg['IA']['service'] == 'poe':
                rep = PoeLLM(verbose, cfg['Database']['type'], cfg['IA']['modele'], api_key=cfg['IA']['api-key'],
                             base_url='https://api.poe.com/v1',
                             bd=sgbd.tables2string()).run(None, None, None)
            elif cfg['IA']['service'] == 'openai':
                rep = OpenaiLLM(verbose, cfg['Database']['type'], cfg['IA']['modele'], api_key=cfg['IA']['api-key'],
                                base_url='https://api.openai.com/v1/chat/completions',
                                bd=sgbd.tables2string()).run(None, None, None)
            elif cfg['IA']['service'] == 'google':
                rep = GoogleLLM(verbose, cfg['Database']['type'], cfg['IA']['modele'], api_key=cfg['IA']['api-key'],
                                base_url='https://generativelanguage.googleapis.com/v1beta/openai/',
                                bd=sgbd.tables2string()).run(None, None, None)
            elif cfg['IA']['service'] == 'generic':
                rep = GenericLLM(verbose, cfg['Database']['type'], cfg['IA']['modele'], api_key=cfg['IA']['api-key'],
                                 base_url=cfg['IA']['url'],
                                 bd=sgbd.tables2string()).run(None, None, None)
            else:
                rep = ""
            saveCache(cache_file, cache, str_sql, rep)
        if not rep:
            cache = loadCache("describe_default.json", duree)
            if str_sql in cache:
                (rep, date) = cache[str_sql]
                rep += f"{BLUE}(cache){RESET}"
            else:
                # gpt-4.1-nano ; gpt-5-nano ; gpt-5.1-codex
                # print("Appel POE 2")
                rep = PoeLLM(verbose, cfg['Database']['type'],
                             "gpt-5-nano", "umnm9e2VrXsAX6FDurYa8ThkRTcYSHuQMzb22xjnh0A",
                             "https://api.poe.com/v1",
                             sgbd.tables2string()).run(None, None, None)
                saveCache("describe_default.json", cache, str_sql, rep)
        clear_line()
        if rep:
            print(f"\n{BLUE}--- Description par IA générative ---{RESET}")
            print(rep)

    print(f"\nDetail de la base de données")
    print(sgbd.tables2string())
    exit(0)


##########################################################################################################
##########################################################################################################
##########################################################################################################
def mysql():
    cfg = readConfigFile()
    parser = argparse.ArgumentParser(
        description="Effectue l'exécution pas à pas d'une requête sur MySQL\n (c) E. Desmontils, Nantes Université, 2024")
    if cfg['Database']['type'] == "mysql":
        port = cfg['Database']['port']
        host = cfg['Database']['host']
        user = cfg['Database']['username']
        password = cfg['Database']['password']
        db = cfg['Database']['database']
        dbConnectArgs(parser, defaultPort=port, defaultHost=host, defaultUser=user)
    else:
        port = 3306
        host = 'localhost'
        user = 'desmontils-e'
        password = ''
        db = None
        dbConnectArgs(parser, defaultPort=port, defaultHost=host, defaultUser=user)

    stdArgs(parser, db)
    args = parser.parse_args()

    port = args.port
    host = args.host
    user = args.user
    db = args.db

    if (args.password is None) and (args.port == cfg['Database']['port']) and (
            args.host == cfg['Database']['host']) and (args.user == cfg['Database']['username']) and (
            args.db == cfg['Database']['database']):
        password = cfg['Database']['password']
    else:
        if args.password is None :
            password = ''
        else:
            password = args.password

    debug = False
    # debug = cfg.getboolean('Autre', 'debug') or args.debug
    verbose = cfg.getboolean('Autre', 'verbose') or args.verbose

    # if debug:
    #    print('Infos BD : ', type, args.user, args.password, args.host, args.port, args.db)
    if args.describe:
        # Affichage des tables de la BD
        try:
            doDescribe(cfg,
                       DBMySQL(db=(user, password, host, db), debug=False, verbose=verbose), args.verbose)
        except Exception as e:
            print(f'Erreur Describe MySQL : {e}')
            exit(1)

    # xAPI configuration
    onLRS = cfg['LRS']['mode'] == 'on'
    if onLRS:
        lrs = LRS(cfg['LRS']['endpoint'], cfg['LRS']['username'], cfg['LRS']['password'], debug=debug)
    else:
        lrs = None

    sqlTXT = getQuery(args)
    if onLRS:
        doSBS((user, password, host, db), 'mysql', db, sqlTXT, debug, verbose, args.step_by_step, lrs)
    else:
        doSBS((user, password, host, db), 'mysql', db, sqlTXT, debug, verbose, args.step_by_step)


##########################################################################################################
##########################################################################################################
##########################################################################################################
def pgsql():
    cfg = readConfigFile()
    parser = argparse.ArgumentParser(
        description="Effectue l'exécution pas à pas d'une requête sur PostgreSQL\n (c) E. Desmontils, Nantes Université, 2024")
    if cfg['Database']['type'] == "pgsql":
        port = cfg['Database']['port']
        host = cfg['Database']['host']
        user = cfg['Database']['username']
        password = cfg['Database']['password']
        db = cfg['Database']['database']
        dbConnectArgs(parser, defaultPort=port, defaultHost=host, defaultUser=user)
    else:
        port = 5432
        host = 'localhost'
        user = 'desmontils-e'
        db = None
        dbConnectArgs(parser, defaultPort=port, defaultHost=host, defaultUser=user)

    stdArgs(parser, db)
    args = parser.parse_args()

    port = args.port
    host = args.host
    user = args.user
    db = args.db

    if (args.password is None) and (args.port == cfg['Database']['port']) and (
            args.host == cfg['Database']['host']) and (args.user == cfg['Database']['username']) and (
            args.db == cfg['Database']['database']):
        password = cfg['Database']['password']
    else:
        if args.password is None :
            password = ''
        else:
            password = args.password

    debug = False
    # debug = cfg.getboolean('Autre', 'debug') or args.debug
    verbose = cfg.getboolean('Autre', 'verbose') or args.verbose

    if args.describe:
        # Affichage des tables de la BD
        try:
            doDescribe(cfg,
                       DBPGSQL(db=f"dbname={db} user={user} password={password} host={host} port={port}", debug=debug,
                               verbose=verbose), args.verbose)
        except Exception as e:
            print(f'Erreur Describe PostgreSQL : {e}')
            exit(1)

    # xAPI configuration
    onLRS = cfg['LRS']['mode'] == 'on'
    if onLRS:
        lrs = LRS(cfg['LRS']['endpoint'], cfg['LRS']['username'], cfg['LRS']['password'], debug=debug)
    else:
        lrs = None

    sqlTXT = getQuery(args)
    if onLRS:
        doSBS(f"dbname={db} user={user} password={password} host={host} port={port}", 'pgsql',
              db, sqlTXT, debug, verbose, args.step_by_step, lrs)
    else:
        doSBS(f"dbname={db} user={user} password={password} host={host} port={port}", 'pgsql',
              db, sqlTXT, debug, verbose, args.step_by_step)


##########################################################################################################
##########################################################################################################
##########################################################################################################
def sqlite():
    cfg = readConfigFile()
    parser = argparse.ArgumentParser(
        description="Effectue l'exécution pas à pas d'une requête sur SQLite\n (c) E. Desmontils, Nantes Université, 2024")

    if cfg['Database']['type'] == "sqlite":
        db = cfg['Database']['database']
    else:
        db = None

    parser = stdArgs(parser, db)
    args = parser.parse_args()
    debug = False
    # debug = cfg.getboolean('Autre', 'debug') or args.debug
    verbose = cfg.getboolean('Autre', 'verbose') or args.verbose

    db = args.db

    if not (existFile(db)):
        if args.verbose: print(f'database file not found : {db}')
        package_files = importlib.resources.files("querycraft.data")
        if args.verbose: print(f'trying to search in default databases')
        if not (existFile(package_files / db)):
            print(f'database file not found')
            exit(1)
        else:
            db = package_files / db
            if args.verbose: print('database exists')
    else:
        if args.verbose: print('database exists')
    # if args.debug:
    #    print('Infos BD : ', type, args.user, args.password, args.host, args.port, args.db)
    if args.describe:
        # Affichage des tables de la BD
        try:
            doDescribe(cfg, DBSQLite(db=str(db), debug=debug, verbose=verbose), args.verbose)
        except Exception as e:
            print(f'Erreur Describe SQLite : {e}')
            exit(1)

    # xAPI configuration
    onLRS = cfg['LRS']['mode'] == 'on'
    if onLRS:
        lrs = LRS(cfg['LRS']['endpoint'], cfg['LRS']['username'], cfg['LRS']['password'], debug=debug)
    else:
        lrs = None

    sqlTXT = getQuery(args)
    if onLRS:
        doSBS(db, 'sqlite', db, sqlTXT, debug, verbose, args.step_by_step, lrs)
    else:
        doSBS(db, 'sqlite', db, sqlTXT, debug, verbose, args.step_by_step)


##########################################################################################################
##########################################################################################################
##########################################################################################################
def parse_assignment(assignment: str):
    """
    Transforme une chaîne 'Section.clef=valeur' en ses composantes.
    """
    try:
        section_key, value = assignment.split("=", 1)
        section, key = section_key.split(".", 1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Format invalide pour --set '{assignment}'. "
            "Utiliser Section.clef=valeur."
        ) from exc
    return section.strip(), key.strip(), value.strip()


def afficher_config(config: ConfigParser) -> None:
    if not config.sections():
        print("Le fichier ne contient aucune section.")
        return

    largeur_section = max(len(section) for section in config.sections())
    largeur_cle = max(
        len(key)
        for section in config.sections()
        for key in config[section].keys()
    )
    # print(largeur_cle)
    for section in config.sections():
        print(f"\n{GREEN}{BOLD}[{section}]{RESET}")
        tab = []
        for key, value in config[section].items():
            # print(f"  {key.ljust(largeur_cle)} : {value}")
            tab.append([key, value])
        print(format_table_2(headers=['Clé', 'Valeur'], rows=tab, table_size=50, min_col_width=largeur_cle))
        if section == "IA":
            print(f"Services reconnus : ollama, poe, openai et generic")


def admin():
    parser = argparse.ArgumentParser(
        description="Met à jour des paramètres du fichier de configuration."
    )
    parser.add_argument(
        "--set",
        nargs="+",
        required=False,
        help="Assignments au format Section.clef=valeur."
    )
    args = parser.parse_args()
    with importlib.resources.path("querycraft.config", "config-sbs.cfg") as config_path:
        config = ConfigParser()
        config.optionxform = str  # respecte la casse des clefs
        config.read(config_path, encoding="utf-8")

        if args.set:
            for assignment in args.set:
                section, key, value = parse_assignment(assignment)
                if section not in config:
                    print(f"Erreur : section '{section}' absente dans {config_path.name}.", file=sys.stderr)
                    sys.exit(1)
                if key not in config[section]:
                    print(f"Erreur : clef '{key}' absente dans la section '{section}'.", file=sys.stderr)
                    sys.exit(1)
                config[section][key] = value

            with config_path.open("w", encoding="utf-8") as config_file:
                config.write(config_file)

            print(f"Fichier {config_path} mis à jour avec succès.")
        else:
            print("Aucune assignation à traiter.")
            afficher_config(config)


##########################################################################################################
##########################################################################################################
##########################################################################################################
def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument('--lrs', help='use en Veracity lrs', action='store_true', default=False)
    parser.add_argument('-v', '--verbose', help='verbose mode', action='store_true', default=False)
    parser.add_argument('--debug', help='debug mode', action='store_true', default=False)
    parser.add_argument('-d', '--db', help='database file (sqlite) or name (others)', default=None)
    parser.add_argument('-nsbs', '--step_by_step', help='step by step mode', action='store_false', default=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', help='sql file')
    group.add_argument('-s', '--sql', type=str, help='sql string', default="")
    group.add_argument('-b', '--describe', help='DB Schema', action='store_true', default=False)

    args = parser.parse_args()
    sqlTXT = getQuery(args)

    # ==================================================
    # === Gestion de la configuration =================
    # ==================================================

    cfg = readConfigFile()

    # Debug ?
    debug = cfg.getboolean('Autre', 'debug') or args.debug
    verbose = cfg.getboolean('Autre', 'verbose') or args.verbose
    if debug:
        print("Mode debug activé")
    package_files = importlib.resources.files("querycraft.data")
    # Database configuration
    if args.db:
        if args.db.endswith('.db'):
            if not (existFile(args.db)):
                if args.verbose:
                    print(f'database file not found : {args.db}')
                    print(f'trying to search in default databases')
                if not (existFile(package_files / args.db)):
                    print(f'database file not found')
                    exit(1)
                else:
                    args.db = package_files / args.db
                    if args.verbose: print('database exists')
            else:
                if args.verbose: print('database exists')
            database = args.db
            if debug: print(f"SQLite database from parameter : {database}")
            type = 'sqlite'
            username = None
            password = None
            host = None
            port = None
        else:
            database = args.db
            if debug: print(f"PGSQL database from parameter : {database}")
            type = 'pgsql'  # Database configuration
            username = 'postgres'
            password = ''
            host = 'localhost'
            port = '5432'
    else:
        type = cfg['Database']['type']
        if type == 'sqlite':
            if debug: print(f"SQLite database from config file : {cfg['Database']['database']}")
            database = package_files / cfg['Database'][
                'database']  # importlib.resources.resource_filename("querycraft.data", cfg['Database']['database'])
            username = None
            password = None
            host = None
            port = None
        else:
            if debug: print(f"{type} database from config file : {cfg['Database']['database']}")
            username = cfg['Database']['username']
            password = cfg['Database']['password']
            host = cfg['Database']['host']
            port = cfg['Database']['port']
            database = cfg['Database']['database']

    # xAPI configuration
    onLRS = cfg['LRS']['mode'] == 'on'
    if onLRS:
        lrs = LRS(cfg['LRS']['endpoint'], cfg['LRS']['username'], cfg['LRS']['password'], debug=debug)
        lrs.setContextSBS()

    # IA configuration
    model = cfg['IA']['modele']
    if debug: print('Modele : ', model)
    SQLQueryException.set_model(cfg['IA']['service'], model, cfg['IA']['api-key'], cfg['IA']['url'],
                                cfg['IA']['mode'], int(cfg['IA']['duree-cache']))

    if debug:
        print('Infos BD : ', type, username, password, host, port, database)

    try:
        try:
            if type is None:
                raise Exception("Configuration non fournie")
            if type == 'sqlite':
                if args.describe:
                    # Affichage des tables de la BD
                    try:
                        db = DBSQLite(db=database, debug=False, verbose=args.verbose, step_by_step=args.step_by_step)
                        print(f"{type}\n{db.tables2string()}")
                        exit(0)
                    except Exception as e:
                        print(f"Erreur Describe SQLite : {e}")
                        exit(1)
                sql = SQL(db=database, dbtype='sqlite', debug=debug, verbose=verbose, step_by_step=args.step_by_step)
            elif type == 'pgsql':  # f"dbname={database} user={username} password={password} host={host} port={port}"
                if args.describe:
                    # Affichage des tables de la BD
                    try:
                        db = DBPGSQL(
                            db=f"dbname={database} user={username} password={password} host={host} port={port}",
                            debug=False, verbose=args.verbose, step_by_step=args.step_by_step)
                        print(f"{type}\n{db.tables2string()}")
                        exit(0)
                    except Exception as e:
                        print(f"Erreur Describe PostgreSQL : {e}")
                        exit(1)
                sql = SQL(f"dbname={database} user={username} password={password} host={host} port={port}",
                          dbtype='pgsql', debug=debug, verbose=verbose, step_by_step=args.step_by_step)
            elif type == 'mysql':  # (username, password, host ,database) # port ????
                if args.describe:
                    # Affichage des tables de la BD
                    try:
                        db = DBMySQL(db=(username, password, host, database), debug=False, verbose=args.verbose,
                                     step_by_step=args.step_by_step)
                        print(f"{type}\n{db.tables2string()}")
                        exit(0)
                    except Exception as e:
                        print(f"Erreur Describe MySQL : {e}")
                        exit(1)
                sql = SQL(db=(username, password, host, database), dbtype='mysql', debug=debug, verbose=verbose,
                          step_by_step=args.step_by_step)
            else:
                raise Exception("Base de données non supportée")

            sql.setSQL(sqlTXT)

            # LRS : envoie du statement
            if onLRS: lrs.sendSBSExecute(type, database, sqlTXT)

        except Exception as e:
            pprint(e)
            # LRS : envoie du statement
            if onLRS: lrs.sendSBSExecute(type, database, sqlTXT, error=e)
            exit()

        sbs(sql, cfg, verbose)  # Pas à pas

        if onLRS: lrs.sendSBSpap(type, database, sqlTXT)

    except Exception as e:
        # LRS : envoie du statement
        if onLRS: lrs.sendSBSpap(type, database, sqlTXT, e)
        print(f'Erreur SBS : {e}')


if __name__ == '__main__':
    main()
