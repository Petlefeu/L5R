#!/usr/bin/python2.7
#-*- coding: utf-8 -*-
""" AI simple de combat L5R
VERSION 6.1.0 """

# from pdb import set_trace as st
from random import randint
import argparse
import sys

# Couleurs
ROUGE = '\033[1;31m'
VERT = '\033[1;32m'
JAUNE = '\033[1;33m'
MAUVE = '\033[1;34m'
ROSE = '\033[1;35m'
CYAN = '\033[1;36m'
BLANC = '\033[m'
NATIVE = '\033[m'
BOLD = '\033[1m'
BU = '\033[1;5m'

def launch_dices(dices_launch, dices_keep, void):
    """ Fonction qui lance les dés """
    # Rééquilibrage Ex: 12k6 => 10k7
    if dices_launch > 10:
        reste = int((dices_launch - 10)/2)
        dices_launch = 10
        if dices_keep+reste > 10:
            dices_keep = 10
        else:
            dices_keep += reste
    dices = []
    void_left = void
    for i in range(dices_launch):
        result = randint(1, 10)
        dices.append(result)
        while result == 10 and void_left > 0:
            void_left -= 1
            result = randint(1, 10)
            dices[i] += result
    dices.sort()
    result = sum(dices[(dices_launch-dices_keep):])
    if ARGS.verbose:
        print "%s[DEBUG] %sk%s = %s%s" % (MAUVE, dices_launch, dices_keep, result, NATIVE)
    return result

def malus(point_vie, terre, custom=None):
    """ Cette fonction calcul le malus
    appliqué aux actions """
    if custom is not None:
        for i in custom:
            if point_vie > i[0]:
                return i[1]
    else:
        malus_point = 0
        if point_vie > 7*terre*2:
            malus_point = 0
        elif point_vie > 6*terre*2:
            malus_point = 3
        elif point_vie > 5*terre*2:
            malus_point = 5
        elif point_vie > 4*terre*2:
            malus_point = 10
        elif point_vie > 3*terre*2:
            malus_point = 15
        elif point_vie > 2*terre*2:
            malus_point = 20
        elif point_vie > 1*terre*2:
            malus_point = 40
        else:
            malus_point = 100
        return malus_point

def detect_death(metadata):
    """ Cette fonction détecte si l'adversaire
    est mort """
    if metadata['point_vie'] <= metadata['terre']*3 and metadata['void_left'] <= 0:
        print '%sAdversaire est hors combat !%s' % (VERT, NATIVE)
        if ARGS.verbose:
            print "%s[DEBUG] +%s Points%s" % (MAUVE, metadata['void_left']*5, NATIVE)
        metadata['points'] += metadata['void_left']*5
        print 'Vous avez %s%s%s points !' % (VERT, metadata['points'], NATIVE)
        print '%s[STATS] Terre: %s, Eau: %s, Air: %s, Feu: %s, Vide: %s%s' % (
            MAUVE, metadata['terre'], metadata['eau'], metadata['air'], metadata['feu'], metadata['void'], NATIVE)
        sys.exit(0)
    elif metadata['point_vie'] <= metadata['terre']*2:
        print '%sAdversaire est hors combat !%s' % (VERT, NATIVE)
        if ARGS.verbose:
            print "%s[DEBUG] +%s Points%s" % (MAUVE, metadata['void_left']*5, NATIVE)
        metadata['points'] += metadata['void_left']*5
        print 'Vous avez %s%s%s points !' % (VERT, metadata['points'], NATIVE)
        print '%s[STATS] Terre: %s, Eau: %s, Air: %s, Feu: %s, Vide: %s%s' % (
            MAUVE, metadata['terre'], metadata['eau'], metadata['air'], metadata['feu'], metadata['void'], NATIVE)
        sys.exit(0)

def do_i_reduct_damage(damage, metadata):
    """ Cette fonction peut reduire les dommages
    grâce à un point de void """
    if metadata['void_left'] > 0 and malus(metadata['point_vie']-int(damage)+metadata['reduction'], metadata['terre']) >= 10:
        new_damage = max(0, int(damage)-10)
        print "Utilisation d'%sun point de VIDE%s, reduction des dommages (%s-10=%s)" % (JAUNE, NATIVE, damage, new_damage)
        return new_damage, metadata
    return damage, metadata

def gen_posture(is_first_to_fight, metadata):
    """ Fonction de génération de posture """
    random_number = randint(0, 3)
    postures_1_ok = ['ASSAUT', 'ASSAUT', 'ATTAQUE', 'ATTAQUE']
    postures_2_ok = ['ESQUIVE', 'ESQUIVE', 'ATTAQUE', 'ATTAQUE']
    postures_mal = ['ASSAUT', 'ASSAUT', 'ASSAUT', 'ATTAQUE']
    metadata['bonus_atk_dl'] = 0
    metadata['bonus_atk_dg'] = 0
    metadata['bonus_tn'] = 0
    if malus(metadata['point_vie'], metadata['terre']) >= 5:
        metadata['posture'] = postures_mal[random_number]
    else:
        if is_first_to_fight:
            metadata['posture'] = postures_1_ok[random_number]
        else:
            metadata['posture'] = postures_2_ok[random_number]
    if metadata['posture'] is "ASSAUT":
        metadata['bonus_atk_dl'] = 2
        metadata['bonus_atk_dg'] = 1
        metadata['bonus_tn'] = -10
    elif metadata['posture'] is "ESQUIVE":
        metadata['bonus_tn'] = int(launch_dices(metadata['skill_defense'] + metadata['air'], metadata['air'], metadata['void'])/2)
    return metadata

def joueur_attaque(metadata):
    """ Attaque du joueur """
    if ARGS.verbose:
        print "%s[DEBUG] AC = %s, BONUS_TN = %s, POSTURE = %s%s" % (MAUVE, metadata['armor_class'], metadata['bonus_tn'], metadata['posture'], NATIVE)
    print "Attaquez. ND=%s, PV=%s (MALUS=%s, REDUC=%s)" % (metadata['armor_class']+metadata['bonus_tn'], metadata['point_vie'], malus(metadata['point_vie'], metadata['terre']), metadata['reduction'])
    dmg = raw_input("Si vous touchez, écrivez les dégâts subits (sinon faites Entrée) : ")
    if dmg is "":
        print "%sVous ne touchez pas l'adversaire%s" % (ROUGE, NATIVE)
        print ""
        return metadata
    dmg, metadata = do_i_reduct_damage(dmg, metadata)
    dmg_real = max(0, int(dmg) - metadata['reduction'])
    metadata['point_vie'] -= dmg_real
    points_add = dmg_real*(metadata['feu']+metadata['terre']+metadata['air']+metadata['eau'])/4
    if ARGS.verbose:
        print "%s[DEBUG] +%s Points%s" % (MAUVE, points_add, NATIVE)
    metadata['points'] += points_add
    print "L'adversaire subit %s%s%s dégâts !" % (VERT, dmg_real, NATIVE)
    print ""
    detect_death(metadata)
    return metadata

def joueur_2e_attaque(metadata):
    """ 2e attaque du joueur """
    var = raw_input("Avez-vous une deuxième attaque ? [y/N/q]")
    if var is 'y':
        return joueur_attaque(metadata)
    elif var is 'q':
        print '%sVous êtes hors combat ...%s' % (ROUGE, NATIVE)
        print 'Vous avez %s%s%s points !' % (ROUGE, metadata['points'], NATIVE)
        print '%s[STATS] Terre: %s, Eau: %s, Air: %s, Feu: %s, Vide: %s, Katana:%sk%s/%sk%s%s' % (
            MAUVE, metadata['terre'], metadata['eau'], metadata['air'], metadata['feu'], metadata['void'],
            metadata['skill_kenjutsu'] + metadata['feu'], metadata['feu'], 4 + metadata['eau'], 3, NATIVE)
        sys.exit(0)
    print ""
    return metadata

def adversaire_attaque(atk_des_lances, atk_des_gardes, dmg_des_lances, dmg_des_gardes, metadata, bonus=0, bonus_atk=0):
    """ Attaque de l'adversaire """
    jet_atk = launch_dices(atk_des_lances, atk_des_gardes, metadata['void'])
    jet_atk_bonus = max(0, (jet_atk - malus(metadata['point_vie'], metadata['terre']) + bonus_atk))
    if ARGS.verbose:
        print "%s[DEBUG] modificateur = %s, total = %s%s" % (MAUVE, (bonus_atk - malus(metadata['point_vie'], metadata['terre'])), jet_atk_bonus, NATIVE)
    print "Adversaire vous attaque et fait %s%s%s" % (ROUGE, jet_atk_bonus, NATIVE)
    var = raw_input("Est-ce qu'il touche ? [Y/n/q]")
    if var is 'n':
        print "%sAdversaire rate son attaque%s" % (VERT, NATIVE)
    elif var is 'q':
        print '%sVous êtes hors combat ...%s' % (ROUGE, NATIVE)
        print 'Vous avez %s%s%s points !' % (ROUGE, metadata['points'], NATIVE)
        print '%s[STATS] Terre: %s, Eau: %s, Air: %s, Feu: %s, Vide: %s, Katana:%sk%s/%sk%s%s' % (
            MAUVE, metadata['terre'], metadata['eau'], metadata['air'], metadata['feu'], metadata['void'],
            metadata['skill_kenjutsu'] + metadata['feu'], metadata['feu'], 4 + metadata['eau'], 3, NATIVE)
        sys.exit(0)
    else:
        dmg_real = int(launch_dices(dmg_des_lances, dmg_des_gardes, metadata['void']) + bonus)
        print "Les dommages sont de %s%s%s" % (ROUGE, dmg_real, NATIVE)
        if ARGS.verbose:
            print "%s[DEBUG] -%s Points%s" % (MAUVE, dmg_real, NATIVE)
        metadata['points'] -= dmg_real
    print ""
    return metadata


def joueur_attaque_shadowland(metadata):
    """ Attaque du joueur """
    if ARGS.verbose:
        print "%s[DEBUG] AC = %s, BONUS_TN = %s, POSTURE = %s%s" % (MAUVE, metadata['armor_class'], metadata['bonus_tn'], metadata['posture'], NATIVE)
    print "Attaquez. ND=%s, PV=%s (MALUS=%s, REDUC=%s)" % (metadata['armor_class']+metadata['bonus_tn'], metadata['point_vie'], malus(metadata['point_vie'], metadata['terre'], custom=metadata['wounds']), metadata['reduction'])
    dmg = raw_input("Si vous touchez, écrivez les dégâts subits (sinon faites Entrée) : ")
    if dmg is "":
        print "%sVous ne touchez pas l'adversaire%s" % (ROUGE, NATIVE)
        print ""
        return metadata
    dmg_real = max(0, int(dmg) - metadata['reduction'])
    metadata['point_vie'] -= dmg_real
    points_add = dmg_real*(metadata['feu']+metadata['terre']+metadata['air']+metadata['eau'])/4
    if ARGS.verbose:
        print "%s[DEBUG] +%s Points%s" % (MAUVE, points_add, NATIVE)
    metadata['points'] += points_add
    print "L'adversaire subit %s%s%s dégâts !" % (VERT, dmg_real, NATIVE)
    print ""
    detect_death(metadata)
    return metadata

def joueur_2e_attaque_shadowland(metadata):
    """ 2e attaque du joueur """
    var = raw_input("Avez-vous une deuxième attaque ? [y/N/q]")
    if var is 'y':
        return joueur_attaque_shadowland(metadata)
    elif var is 'q':
        print '%sVous êtes hors combat ...%s' % (ROUGE, NATIVE)
        print 'Vous avez %s%s%s points !' % (ROUGE, metadata['points'], NATIVE)
        print '%s[STATS] Terre: %s, Eau: %s, Air: %s, Feu: %s, Vide: %s, Masse:5k3/8k2%s' % (
            MAUVE, metadata['terre'], metadata['eau'], metadata['air'], metadata['feu'], metadata['void'], NATIVE)
        sys.exit(0)
    print ""
    return metadata

def adversaire_attaque_shadowland(atk_des_lances, atk_des_gardes, dmg_des_lances, dmg_des_gardes, metadata, bonus=0, bonus_atk=0):
    """ Attaque de l'adversaire """
    jet_atk = launch_dices(atk_des_lances, atk_des_gardes, metadata['void'])
    jet_atk_bonus = max(0, (jet_atk - malus(metadata['point_vie'], metadata['terre'], custom=metadata['wounds']) + bonus_atk))
    if ARGS.verbose:
        print "%s[DEBUG] modificateur = %s, total = %s%s" % (MAUVE, (bonus_atk - malus(metadata['point_vie'], metadata['terre'], custom=metadata['wounds'])), jet_atk_bonus, NATIVE)
    print "Adversaire vous attaque et fait %s%s%s" % (ROUGE, jet_atk_bonus, NATIVE)
    var = raw_input("Est-ce qu'il touche ? [Y/n/q]")
    if var is 'n':
        print "%sAdversaire rate son attaque%s" % (VERT, NATIVE)
    elif var is 'q':
        print '%sVous êtes hors combat ...%s' % (ROUGE, NATIVE)
        print 'Vous avez %s%s%s points !' % (ROUGE, metadata['points'], NATIVE)
        print '%s[STATS] Terre: %s, Eau: %s, Air: %s, Feu: %s, Vide: %s, Masse:5k3/8k2%s' % (
            MAUVE, metadata['terre'], metadata['eau'], metadata['air'], metadata['feu'], metadata['void'], NATIVE)
        sys.exit(0)
    else:
        dmg_real = int(launch_dices(dmg_des_lances, dmg_des_gardes, metadata['void']) + bonus)
        print "Les dommages sont de %s%s%s" % (ROUGE, dmg_real, NATIVE)
        if ARGS.verbose:
            print "%s[DEBUG] -%s Points%s" % (MAUVE, dmg_real, NATIVE)
        metadata['points'] -= dmg_real
        taint = raw_input("L'arme est %ssouillée%s, faites un jet de %sTerre%s pur (ND=15): " % (JAUNE, NATIVE, JAUNE, NATIVE))
        if taint is "":
            taint = 0
        if int(taint) >= 15:
            print "%sVous n'êtes pas souillé!%s" % (VERT, NATIVE)
            print ""
        else:
            print "%sVous êtes souillé...%s" % (ROUGE, NATIVE)
    print ""
    return metadata


def ronin(modifier):
    """ Un ronin stratège
    Changement de posture
    Utilisation du void pour se défendre
    """
    meta_modifier = 0
    if ARGS.randomize:
        meta_modifier = randint(-1, 1)
    metadata = {
        'terre': 1 + modifier,
        'air'  : 1 + modifier - meta_modifier,
        'eau'  : 1 + modifier + meta_modifier,
        'feu'  : 1 + modifier - meta_modifier,
        'void' : 1 + modifier,
        'void_left': modifier,
        'rank' : modifier,
        'armor_class': 5+(1+modifier)*5+5,
        'point_vie': 5*(1+modifier)+7*(1+modifier)*2,
        'reduction': 3,
        'skill_defense': modifier,
        'skill_kenjutsu': 2 + modifier,
        'init': 0,
        'posture': None,
        'bonus_atk_dl': 0,
        'bonus_atk_dg': 0,
        'bonus_tn': 0,
        'points': 0,
    }
    print "%sSuzuki%s (Ronin rang %s)" % (JAUNE, NATIVE, metadata['rank'])
    if ARGS.verbose:
        print '%s[DEBUG] Terre: %s, Eau: %s, Air: %s, Feu: %s, Vide: %s, Katana:%sk%s/%sk%s%s' % (
            MAUVE, metadata['terre'], metadata['eau'], metadata['air'], metadata['feu'], metadata['void'],
            metadata['skill_kenjutsu'] + metadata['feu'], metadata['feu'], 4 + metadata['eau'], 3, NATIVE)
    ini = raw_input("Entrez votre initiative : ")
    if ini is "":
        ini = 0
    metadata['init'] = launch_dices(metadata['air'] + metadata['rank'], metadata['air'], metadata['void'])
    print "L'initiative de votre adversaire est de %s%s%s" % (JAUNE, metadata['init'], NATIVE)
    if ARGS.verbose:
        print "%s[DEBUG] %s Points%s" % (MAUVE, int(ini) - metadata['init'], NATIVE)
    metadata['points'] = int(ini) - metadata['init']

    # Premier tour
    if int(ini) >= metadata['init']:
        print "%sVous commencez en premier.%s" % (VERT, NATIVE)
        print ""
        # CHOIX de la POSTURE
        metadata = gen_posture(False, metadata)
        raw_input("La posture de l'adversaire est %s%s%s. Choisissez la votre." % (JAUNE, metadata['posture'], NATIVE))

        # ATTAQUE JOUEUR
        metadata = joueur_attaque(metadata)

        # ATTAQUE ADVERSAIRE
        if metadata['posture'] is "ESQUIVE":
            print "L'Adversaire se protège !"
        else:
            metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 4 + metadata['eau'], 3, metadata)

        # 2e ATTAQUE JOUEUR
        metadata = joueur_2e_attaque(metadata)

        # En boucle
        while metadata['point_vie'] > 0:
            if ARGS.verbose:
                print "%s[DEBUG] -5 Points%s" % (MAUVE, NATIVE)
            metadata['points'] -= 5
            # CHOIX de la POSTURE JOUEUR
            raw_input("Choisissez votre posture.")
            # ATTAQUE JOUEUR
            metadata = joueur_attaque(metadata)

            # CHOIX POSTURE ADVERSAIRE
            metadata = gen_posture(False, metadata)
            # ATTAQUE ADVERSAIRE
            print "La posture de l'adversaire est %s%s%s." % (JAUNE, metadata['posture'], NATIVE)
            if metadata['posture'] is "ESQUIVE":
                print "L'Adversaire se protège !"
            else:
                metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

            # 2e ATTAQUE JOUEUR
            metadata = joueur_2e_attaque(metadata)
    else:
        print "%sL'Adversaire commence en premier%s" % (ROUGE, NATIVE)
        print ""
        # CHOIX de la POSTURE
        metadata = gen_posture(True, metadata)
        raw_input("La posture de l'adversaire est %s%s%s. Choisissez la votre." % (JAUNE, metadata['posture'], NATIVE))

        # ATTAQUE ADVERSAIRE
        if metadata['posture'] is "ESQUIVE":
            print "L'Adversaire se protège !"
        else:
            metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

        # ATTAQUE JOUEUR
        metadata = joueur_attaque(metadata)
        # 2e ATTAQUE JOUEUR
        metadata = joueur_2e_attaque(metadata)

        # En boucle
        while metadata['point_vie'] > 0:
            if ARGS.verbose:
                print "%s[DEBUG] -5 Points%s" % (MAUVE, NATIVE)
            metadata['points'] -= 5
            # CHOIX de la POSTURE ADVERSAIRE
            metadata = gen_posture(True, metadata)
            # ATTAQUE ADVERSAIRE
            print "La posture de l'adversaire est %s%s%s." % (JAUNE, metadata['posture'], NATIVE)
            if metadata['posture'] is "ESQUIVE":
                print "L'Adversaire se protège !"
            else:
                metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

            # CHOIX de la POSTURE JOUEUR
            raw_input("Choisissez votre posture.")
            # ATTAQUE JOUEUR
            metadata = joueur_attaque(metadata)
            # 2e ATTAQUE JOUEUR
            metadata = joueur_2e_attaque(metadata)

def hida_samui():
    """ Samui HIDA, rang 3
    PAS de void
    """
    metadata = {
        'nom': 'Samui Hida',
        'terre': 3,
        'air'  : 3,
        'eau'  : 3,
        'void' : 3,
        'void_left': 0,
        'feu'  : 3,
        'rank' : 3,
        'armor_class': 30,
        'point_vie': 57,
        'reduction': 8,
        'skill_defense': 3,
        'skill_kenjutsu': 5,
        'init': 0,
        'posture': None,
        'bonus_atk_dl': 0,
        'bonus_atk_dg': 0,
        'bonus_tn': 0,
        'points': 0
    }
    print "%s%s%s (rang 3)" % (JAUNE, metadata['nom'], NATIVE)
    ini = raw_input("Entrez votre initiative : ")
    if ini is "":
        ini = 0
    metadata['init'] = launch_dices(metadata['air'] + metadata['rank'], metadata['air'], metadata['void'])
    print "L'initiative de %s est de %s%s%s" % (metadata['nom'], JAUNE, metadata['init'], NATIVE)
    metadata['points'] = int(ini) - metadata['init']

    # Premier tour
    if int(ini) >= metadata['init']:
        print "%sVous commencez en premier.%s" % (VERT, NATIVE)
        metadata['points'] += 5
        print ""
        # CHOIX de la POSTURE
        metadata = gen_posture(False, metadata)
        raw_input("La posture de %s est %s%s%s. Choisissez la votre." % (metadata['nom'], JAUNE, metadata['posture'], NATIVE))

        # ATTAQUE JOUEUR
        metadata = joueur_attaque(metadata)

        # ATTAQUE ADVERSAIRE
        if metadata['posture'] is "ESQUIVE":
            print "%s se protège !" % metadata['nom']
        else:
            metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

        # 2e ATTAQUE JOUEUR
        metadata = joueur_2e_attaque(metadata)

        # 2e ATTAQUE ADVERSAIRE
        if metadata['posture'] is not "ESQUIVE":
            print "%s a une deuxième attaque." % metadata['nom']
            metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

        # En boucle
        while metadata['point_vie'] > 0:
            metadata['points'] -= 5
            # CHOIX de la POSTURE JOUEUR
            raw_input("Choisissez votre posture.")
            # ATTAQUE JOUEUR
            metadata = joueur_attaque(metadata)

            # CHOIX POSTURE ADVERSAIRE
            metadata = gen_posture(False, metadata)
            # ATTAQUE ADVERSAIRE
            print "La posture de %s est %s%s%s." % (metadata['nom'], JAUNE, metadata['posture'], NATIVE)
            if metadata['posture'] is "ESQUIVE":
                print "%s se protège !" % metadata['nom']
            else:
                metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

            # 2e ATTAQUE JOUEUR
            metadata = joueur_2e_attaque(metadata)

            # 2e ATTAQUE ADVERSAIRE
            if metadata['posture'] is not "ESQUIVE":
                print "%s a une deuxième attaque." % metadata['nom']
                metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

    else:
        print "%s%s commence en premier%s" % (ROUGE, metadata['nom'], NATIVE)
        metadata['points'] -= 5
        print ""
        # CHOIX de la POSTURE
        metadata = gen_posture(True, metadata)
        raw_input("La posture de %s est %s%s%s. Choisissez la votre." % (metadata['nom'], JAUNE, metadata['posture'], NATIVE))

        # ATTAQUE ADVERSAIRE
        if metadata['posture'] is "ESQUIVE":
            print "%s se protège !" % metadata['nom']
        else:
            metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

        # ATTAQUE JOUEUR
        metadata = joueur_attaque(metadata)

        # 2e ATTAQUE ADVERSAIRE
        if metadata['posture'] is not "ESQUIVE":
            print "%s a une deuxième attaque." % metadata['nom']
            metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

        # 2e ATTAQUE JOUEUR
        metadata = joueur_2e_attaque(metadata)

        # En boucle
        while metadata['point_vie'] > 0:
            metadata['points'] -= 5
            # CHOIX de la POSTURE ADVERSAIRE
            metadata = gen_posture(True, metadata)
            # ATTAQUE ADVERSAIRE
            print "La posture de %s est %s%s%s." % (metadata['nom'], JAUNE, metadata['posture'], NATIVE)
            if metadata['posture'] is "ESQUIVE":
                print "%s se protège !" % metadata['nom']
            else:
                metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

            # CHOIX de la POSTURE JOUEUR
            raw_input("Choisissez votre posture.")
            # ATTAQUE JOUEUR
            metadata = joueur_attaque(metadata)

            # 2e ATTAQUE ADVERSAIRE
            if metadata['posture'] is not "ESQUIVE":
                print "%s a une deuxième attaque." % metadata['nom']
                metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

            # 2e ATTAQUE JOUEUR
            metadata = joueur_2e_attaque(metadata)

def tsurushi_akira(modifier):
    """ Askira TSURUSHI, rang 3
    Utilisation du void
    """
    metadata = {
        'nom': 'Akira Tsurushi',
        'terre': 2,
        'air'  : 3,
        'eau'  : 3,
        'void' : 3,
        'void_left': 3,
        'feu'  : 3,
        'rank' : 3,
        'armor_class': 35,
        'point_vie': 38,
        'reduction': 3,
        'init': 0,
        'posture': None,
        'bonus_atk_dl': 0,
        'bonus_atk_dg': 0,
        'bonus_tn': 0,
        'distance': modifier*5,
        'points': 0
    }
    print "%s%s%s (rang 3)" % (JAUNE, metadata['nom'], NATIVE)
    ini = raw_input("Entrez votre initiative : ")
    if ini is "":
        ini = 0
    metadata['init'] = int(ini) + 5
    print "L'initiative de %s est de %s%s%s." % (metadata['nom'], JAUNE, metadata['init'], NATIVE)
    # Premier tour
    print "%s%s commence en premier.%s" % (ROUGE, metadata['nom'], NATIVE)
    print ""
    # CHOIX de la POSTURE
    metadata['posture'], metadata['bonus_tn'] = ['ATTAQUE', 0]
    if metadata['distance'] > 0:
        print "%s est à %sm de vous. Vous ne pouvez avancer que de 3m en DEFENSE, 5m en ATTAQUE et 10m ASSAUT." % (metadata['nom'], metadata['distance'])
    raw_input("La posture de %s est %s%s%s. Choisissez la votre." % (metadata['nom'], JAUNE, metadata['posture'], NATIVE))

    # ATTAQUE ADVERSAIRE
    if metadata['distance'] > 0:
        metadata = adversaire_attaque(7, 3, 8, 2, metadata)
    else:
        metadata = adversaire_attaque(7, 3, 8, 2, metadata, bonus_atk=-10)

    if metadata['distance'] > 0:
        avance = raw_input("De combien de mètres avancez-vous ? ")
        if avance is "":
            print "%sVous n'avancez pas.%s" % (ROUGE, NATIVE)
            avance = 0
        metadata['distance'] -= int(avance)
        metadata['points'] += int(avance)*2
        print ""
    if metadata['distance'] <= 0:
        # ATTAQUE JOUEUR
        metadata = joueur_attaque(metadata)
        # 2e ATTAQUE JOUEUR
        metadata = joueur_2e_attaque(metadata)


    # En boucle
    while metadata['point_vie'] > 0:
        metadata['points'] -= 5
        # CHOIX de la POSTURE ADVERSAIRE
        metadata['posture'], metadata['bonus_tn'] = ['ATTAQUE', 0]
        # ATTAQUE ADVERSAIRE
        print "La posture de l'adversaire est %s%s%s." % (JAUNE, metadata['posture'], NATIVE)
        if metadata['distance'] > 0:
            metadata = adversaire_attaque(7, 3, 8, 2, metadata)
        else:
            metadata = adversaire_attaque(7, 3, 8, 2, metadata, bonus_atk=-10)

        # CHOIX de la POSTURE JOUEUR
        if metadata['distance'] > 0:
            print "L'adversaire est à %sm de vous. Vous ne pouvez avancer que de 3m en DEFENSE, 5m en ATTAQUE et 10m ASSAUT." % metadata['distance']
        raw_input("Choisissez votre posture.")
        if metadata['distance'] > 0:
            avance = raw_input("De combien de mètres avancez-vous ? ")
            if avance is "":
                print "%sVous n'avancez pas.%s" % (ROUGE, NATIVE)
                avance = 0
            metadata['distance'] -= int(avance)
            metadata['points'] += int(avance)*2
            print ""
        if metadata['distance'] <= 0:
            # ATTAQUE JOUEUR
        # ATTAQUE JOUEUR
            metadata = joueur_attaque(metadata)
            # 2e ATTAQUE JOUEUR
            metadata = joueur_2e_attaque(metadata)

def shadowland(modifier):
    """ Créatures de l'outremonde
    """
    if modifier == 1:
        metadata = {
            'nom': 'Goblin',
            'terre': 1,
            'air'  : 1,
            'eau'  : 1,
            'feu'  : 1,
            'void' : 0,
            'void_left': 0,
            'rank' : 1,
            'armor_class': 15,
            'point_vie': 18,
            'reduction': 3,
            'init': 0,
            'posture': None,
            'bonus_atk_dl': 0,
            'bonus_atk_dg': 0,
            'bonus_tn': 0,
            'points': 0,
            'fear': 0,
            'taint': 2,
            'wounds': [(9, 0), (0, 5)],
            'atk_l': 4,
            'atk_g': 2,
            'dmg_l': 4,
            'dmg_g': 2,
            'arme': 'Couteau',
            'init_l': 3,
            'init_g': 3,
            '2e_att': False,
        }
    elif modifier == 2:
        metadata = {
            'nom': 'Ogre',
            'terre': 3,
            'air'  : 1,
            'eau'  : 2,
            'feu'  : 3,
            'void' : 0,
            'void_left': 0,
            'rank' : 2,
            'armor_class': 25,
            'point_vie': 80,
            'reduction': 10,
            'init': 0,
            'posture': None,
            'bonus_atk_dl': 0,
            'bonus_atk_dg': 0,
            'bonus_tn': 0,
            'points': 0,
            'fear': 2,
            'taint': 3,
            'wounds': [(60, 0), (40, 5), (20, 10), (0, 15)],
            'atk_l': 5,
            'atk_g': 4,
            'dmg_l': 8,
            'dmg_g': 2,
            'arme': 'Masse',
            'init_l': 4,
            'init_g': 3,
            '2e_att': False,
        }
    elif modifier >= 3:
        metadata = {
            'nom': 'Oni',
            'terre': 6,
            'air'  : 1,
            'eau'  : 2,
            'feu'  : 2,
            'void' : 0,
            'void_left': 0,
            'rank' : modifier,
            'armor_class': 10,
            'skill_kenjutsu': 0,
            'point_vie': 41*modifier,
            'reduction': 18+modifier*2,
            'init': 0,
            'posture': None,
            'bonus_atk_dl': 0,
            'bonus_atk_dg': 0,
            'bonus_tn': 0,
            'points': 0,
            'fear': modifier,
            'taint': 2*modifier,
            'wounds': [(31*modifier, 0), (20*modifier, 5), (9*modifier, 10), (0, 15)],
            'atk_l': 4+modifier,
            'atk_g': int(2+modifier/2),
            'dmg_l': 6+modifier,
            'dmg_g': int(1+modifier/2),
            'arme': 'Griffes',
            'init_l': modifier,
            'init_g': modifier-2,
            '2e_att': True,
        }
    print "%s%s%s (équivalent rang %s)" % (JAUNE, metadata['nom'], NATIVE, metadata['rank'])
    if ARGS.verbose:
        print '%s[DEBUG] Terre: %s, Eau: %s, Air: %s, Feu: %s, Vide: %s, %s:%sk%s/%sk%s%s' % (
            MAUVE, metadata['terre'], metadata['eau'], metadata['air'], metadata['feu'], metadata['void'],
            metadata['arme'], metadata['atk_l'], metadata['atk_g'], metadata['dmg_l'], metadata['dmg_g'], NATIVE)

    # PEUR
    if metadata['fear'] > 0:
        peur = raw_input("L'%s fait peur, faites un jet de %sVolonté%s pur, en rajoutant votre %sHonneur%s (ND=%s): " % (metadata['nom'], JAUNE, NATIVE, JAUNE, NATIVE, 5+5*metadata['fear']))
        if peur is "":
            peur = 0
        if int(peur) >= 5+5*metadata['fear']:
            print "%sVous n'avez pas peur!%s" % (VERT, NATIVE)
            print ""
        else:
            print "%sVous avez peur...%s" % (ROUGE, NATIVE)
            print "Vous souffez d'une pénalité de %s%sk0%s sur tous vos jets..." % (ROUGE, metadata['fear'], NATIVE)

    # INITIATIVE
    ini = raw_input("Entrez votre initiative : ")
    if ini is "":
        ini = 0
    metadata['init'] = launch_dices(metadata['init_l'], metadata['init_g'], 0)
    print "L'initiative de votre adversaire est de %s%s%s" % (JAUNE, metadata['init'], NATIVE)
    if ARGS.verbose:
        print "%s[DEBUG] %s Points%s" % (MAUVE, int(ini) - metadata['init'], NATIVE)
    metadata['points'] = int(ini) - metadata['init']

    # Premier tour
    if int(ini) >= metadata['init']:
        print "%sVous commencez en premier.%s" % (VERT, NATIVE)
        print ""
        # CHOIX de la POSTURE
        metadata['posture'], metadata['bonus_tn'] = ['ATTAQUE', 0]
        raw_input("La posture de l'adversaire est %s%s%s. Choisissez la votre." % (JAUNE, metadata['posture'], NATIVE))

        # ATTAQUE JOUEUR
        metadata = joueur_attaque_shadowland(metadata)

        # ATTAQUE ADVERSAIRE
        metadata = adversaire_attaque_shadowland(metadata['atk_l'], metadata['atk_g'], metadata['dmg_l'], metadata['dmg_g'], metadata)

        # 2e ATTAQUE JOUEUR
        metadata = joueur_2e_attaque_shadowland(metadata)

        # 2e ATTAQUE ADVERSAIRE
        if metadata['2e_att']:
            print "%s%s attaque une nouvelle fois !%s" % (ROUGE, metadata['nom'], NATIVE)
            metadata = adversaire_attaque_shadowland(metadata['atk_l'], metadata['atk_g'], metadata['dmg_l'], metadata['dmg_g'], metadata)

        # En boucle
        while metadata['point_vie'] > 0:
            if ARGS.verbose:
                print "%s[DEBUG] -5 Points%s" % (MAUVE, NATIVE)
            metadata['points'] -= 5
            # CHOIX de la POSTURE JOUEUR
            raw_input("Choisissez votre posture.")
            # ATTAQUE JOUEUR
            metadata = joueur_attaque_shadowland(metadata)

            # CHOIX POSTURE ADVERSAIRE
            metadata['posture'], metadata['bonus_tn'] = ['ATTAQUE', 0]
            # ATTAQUE ADVERSAIRE
            print "La posture de l'adversaire est %s%s%s." % (JAUNE, metadata['posture'], NATIVE)
            metadata = adversaire_attaque_shadowland(metadata['atk_l'], metadata['atk_g'], metadata['dmg_l'], metadata['dmg_g'], metadata)

            # 2e ATTAQUE JOUEUR
            metadata = joueur_2e_attaque_shadowland(metadata)

            # 2e ATTAQUE ADVERSAIRE
            if metadata['2e_att']:
                print "%s%s attaque une nouvelle fois !%s" % (ROUGE, metadata['nom'], NATIVE)
                metadata = adversaire_attaque_shadowland(metadata['atk_l'], metadata['atk_g'], metadata['dmg_l'], metadata['dmg_g'], metadata)

    else:
        print "%sL'Adversaire commence en premier%s" % (ROUGE, NATIVE)
        print ""
        # CHOIX de la POSTURE
        metadata['posture'], metadata['bonus_tn'] = ['ATTAQUE', 0]
        raw_input("La posture de l'adversaire est %s%s%s. Choisissez la votre." % (JAUNE, metadata['posture'], NATIVE))

        # ATTAQUE ADVERSAIRE
        metadata = adversaire_attaque_shadowland(metadata['atk_l'], metadata['atk_g'], metadata['dmg_l'], metadata['dmg_g'], metadata)

        # ATTAQUE JOUEUR
        metadata = joueur_attaque_shadowland(metadata)

        # 2e ATTAQUE ADVERSAIRE
        if metadata['2e_att']:
            print "%s%s attaque une nouvelle fois !%s" % (ROUGE, metadata['nom'], NATIVE)
            metadata = adversaire_attaque_shadowland(metadata['atk_l'], metadata['atk_g'], metadata['dmg_l'], metadata['dmg_g'], metadata)

        # 2e ATTAQUE JOUEUR
        metadata = joueur_2e_attaque_shadowland(metadata)

        # En boucle
        while metadata['point_vie'] > 0:
            if ARGS.verbose:
                print "%s[DEBUG] -5 Points%s" % (MAUVE, NATIVE)
            metadata['points'] -= 5
            # CHOIX POSTURE ADVERSAIRE
            metadata['posture'], metadata['bonus_tn'] = ['ATTAQUE', 0]
            # ATTAQUE ADVERSAIRE
            print "La posture de l'adversaire est %s%s%s." % (JAUNE, metadata['posture'], NATIVE)
            metadata = adversaire_attaque_shadowland(metadata['atk_l'], metadata['atk_g'], metadata['dmg_l'], metadata['dmg_g'], metadata)

            # CHOIX de la POSTURE JOUEUR
            raw_input("Choisissez votre posture.")
            # ATTAQUE JOUEUR
            metadata = joueur_attaque_shadowland(metadata)

            # 2e ATTAQUE ADVERSAIRE
            if metadata['2e_att']:
                print "%s%s attaque une nouvelle fois !%s" % (ROUGE, metadata['nom'], NATIVE)
                metadata = adversaire_attaque_shadowland(metadata['atk_l'], metadata['atk_g'], metadata['dmg_l'], metadata['dmg_g'], metadata)

            # 2e ATTAQUE JOUEUR
            metadata = joueur_2e_attaque_shadowland(metadata)

# def monk():
#     """ Tori : Moine
#     """
#     metadata = {
#         'terre': 3,
#         'air'  : 3,
#         'eau'  : 2,
#         'feu'  : 4,
#         'void' : 6,
#         'void_left': 6,
#         'rank' : 3,
#         'armor_class': 22,
#         'point_vie': 57,
#         'reduction': 0,
#         'skill_defense': 3,
#         'init': 0,
#         'posture': None,
#         'bonus_atk_dl': 0,
#         'bonus_atk_dg': 0,
#         'bonus_tn': 0,
#         'points': 0,
#     }
#     print "%sTori%s (Moine rang %s)" % (JAUNE, NATIVE, metadata['rank'])
#     if ARGS.verbose:
#         print '%s[DEBUG] Terre: %s, Eau: %s, Air: %s, Feu: %s, Vide: %s, Bo:%sk%s/%sk%s%s' % (
#             MAUVE, metadata['terre'], metadata['eau'], metadata['air'], metadata['feu'], metadata['void'],
#             8, 4, 4, 2, NATIVE)
#     ini = raw_input("Entrez votre initiative : ")
#     if ini is "":
#         ini = 0
#     metadata['init'] = launch_dices(metadata['air'] + metadata['rank'], metadata['air'], metadata['void'])
#     print "L'initiative de votre adversaire est de %s%s%s" % (JAUNE, metadata['init'], NATIVE)
#     if ARGS.verbose:
#         print "%s[DEBUG] %s Points%s" % (MAUVE, int(ini) - metadata['init'], NATIVE)
#     metadata['points'] = int(ini) - metadata['init']

#     # Premier tour
#     if int(ini) >= metadata['init']:
#         print "%sVous commencez en premier.%s" % (VERT, NATIVE)
#         print ""
#         # CHOIX de la POSTURE
#         metadata['posture'], metadata['bonus_tn'] = ['ESQUIVE', int(launch_dices(metadata['skill_defense'] + metadata['air'], metadata['air'], metadata['void'])/2)]
#         raw_input("La posture de l'adversaire est %s%s%s. Choisissez la votre." % (JAUNE, metadata['posture'], NATIVE))

#         # ATTAQUE JOUEUR
#         metadata = joueur_attaque(metadata)

#         # ATTAQUE ADVERSAIRE
#         print "L'Adversaire se protège !"
#         print "Tori active le %sKiho : 'Ame des quatres vents'%s grâce à un point de vide." % (JAUNE, NATIVE)
#         metadata['void_left'] -= 1
#         metadata['armor_class'] += metadata['rank'] + metadata['air']
#         print "Tori active le %sKiho : 'Danse des Flammes'%s grâce à un point de vide." % (JAUNE, NATIVE)
#         metadata['void_left'] -= 1
#         flame_fist_throw = launch_dices(6, 3, metadata['void'])
#         if flame_fist_throw >= 15:
#             print "Tori active le %sKiho : 'Poing de Feu'%s." % (JAUNE, NATIVE)
#         if metadata['armor_class']+metadata['bonus_tn'] < 40:
#             print "Tori dépense un point de vide pour augmenter son ND de 10."
#             metadata['void_left'] -= 1
#             metadata['bonus_tn'] += 10

#         # 2e ATTAQUE JOUEUR
#         metadata = joueur_2e_attaque(metadata)

#         # En boucle
#         while metadata['point_vie'] > 0:
#             if ARGS.verbose:
#                 print "%s[DEBUG] -5 Points%s" % (MAUVE, NATIVE)
#             metadata['points'] -= 5
#             # CHOIX de la POSTURE JOUEUR
#             raw_input("Choisissez votre posture.")
#             # ATTAQUE JOUEUR
#             metadata = joueur_attaque(metadata)

#             # CHOIX POSTURE ADVERSAIRE
#             metadata = gen_posture(False, metadata)
#             # ATTAQUE ADVERSAIRE
#             print "La posture de l'adversaire est %s%s%s." % (JAUNE, metadata['posture'], NATIVE)
#             if metadata['posture'] is "ESQUIVE":
#                 print "L'Adversaire se protège !"
#             else:
#                 metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

#             # 2e ATTAQUE JOUEUR
#             metadata = joueur_2e_attaque(metadata)
#     else:
#         print "%sL'Adversaire commence en premier%s" % (ROUGE, NATIVE)
#         print ""
#         # CHOIX de la POSTURE
#         metadata = gen_posture(True, metadata)
#         raw_input("La posture de l'adversaire est %s%s%s. Choisissez la votre." % (JAUNE, metadata['posture'], NATIVE))

#         # ATTAQUE ADVERSAIRE
#         if metadata['posture'] is "ESQUIVE":
#             print "L'Adversaire se protège !"
#         else:
#             metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

#         # ATTAQUE JOUEUR
#         metadata = joueur_attaque(metadata)
#         # 2e ATTAQUE JOUEUR
#         metadata = joueur_2e_attaque(metadata)

#         # En boucle
#         while metadata['point_vie'] > 0:
#             if ARGS.verbose:
#                 print "%s[DEBUG] -5 Points%s" % (MAUVE, NATIVE)
#             metadata['points'] -= 5
#             # CHOIX de la POSTURE ADVERSAIRE
#             metadata = gen_posture(True, metadata)
#             # ATTAQUE ADVERSAIRE
#             print "La posture de l'adversaire est %s%s%s." % (JAUNE, metadata['posture'], NATIVE)
#             if metadata['posture'] is "ESQUIVE":
#                 print "L'Adversaire se protège !"
#             else:
#                 metadata = adversaire_attaque(metadata['skill_kenjutsu'] + metadata['feu'] + metadata['bonus_atk_dl'], metadata['feu'] + metadata['bonus_atk_dg'], 5 + metadata['eau'], 3, metadata)

#             # CHOIX de la POSTURE JOUEUR
#             raw_input("Choisissez votre posture.")
#             # ATTAQUE JOUEUR
#             metadata = joueur_attaque(metadata)
#             # 2e ATTAQUE JOUEUR
#             metadata = joueur_2e_attaque(metadata)


def usage():
    """ Aide """
    print '%s <# adversaire> <difficultée>' % sys.argv[0]
    print 'adversaires : 1 - Ronin (difficulté = rang)'
    print '              2 - Samui Hida'
    print '              3 - Akira Tsurushi (difficulté*5m de distance)'
    sys.exit(1)


PARSER = argparse.ArgumentParser(
    description='Description du Programme',
    prog='l5r_combat_simulator')
PARSER.add_argument(
    'adversaire',
    nargs=1,
    metavar='<adversaire>',
    help="%sChoix de l'adversaire: \
      1 - Suzuki Ronin, \
      2 - Samui Hida (rang 3), \
      3 - Akira Tsurushi (rang 3), \
      4 - outremonde (goblin 1, ogre 2, oni 3) \
      5 - Moine%s" % (VERT, NATIVE))
PARSER.add_argument(
    '--verbose',
    action='store_true',
    help="%sVerbosity%s" % (VERT, NATIVE))
PARSER.add_argument(
    '--randomize',
    action='store_true',
    help="%sAjout d'un peu d'alea dans la génération%s" % (VERT, NATIVE))
PARSER.add_argument(
    '--level',
    nargs=1,
    metavar='<rang>',
    help="%sReglage de la difficulté. (1, 2, 3, ...)%s" % (VERT, NATIVE))
ARGS = PARSER.parse_args()
ADVERSAIRE = int(ARGS.adversaire[0])

if ADVERSAIRE == 1:
    try:
        ronin(int(ARGS.level[0]))
    except TypeError:
        PARSER.print_help()
elif ADVERSAIRE == 2:
    hida_samui()
elif ADVERSAIRE == 3:
    try:
        tsurushi_akira(int(ARGS.level[0]))
    except TypeError:
        PARSER.print_help()
elif ADVERSAIRE == 4:
    shadowland(int(ARGS.level[0]))
elif ADVERSAIRE == 5:
    monk()
else:
    PARSER.print_help()
