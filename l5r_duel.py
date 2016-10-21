#!/usr/bin/python2.7
#-*- coding: utf-8 -*-
""" AI simple de combat L5R
VERSION 1.0.0 """

# from pdb import set_trace as st
from random import randint
import sys
from numpy import zeros

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
    dices = zeros(dices_launch)
    void_left = void
    for i in range(dices_launch):
        result = randint(1, 10)
        dices[i] = result
        while result == 10 and void_left > 0:
            void_left -= 1
            result = randint(1, 10)
            dices[i] += result
    dices.sort()
    return sum(dices[(dices_launch-dices_keep):])

def malus(point_vie, terre):
    """ Cette fonction calcul le malus
    appliqué aux actions """
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
        malus_point = 9999999
    return malus_point

def detect_death(point_vie, terre):
    """ Cette fonction détecte si l'adversaire
    est mort """
    if point_vie <= terre*2:
        print '%sAdversaire est hors combat !%s' % (VERT, NATIVE)
        sys.exit(0)

def do_i_reduct_damage(damage, point_vie, terre, void_left, reduction):
    """ Cette fonction peut reduire les dommages
    grâce à un point de vide """
    if void_left > 0 and malus(point_vie-int(damage)+reduction, terre) >= 10:
        new_damage = max(0, int(damage)-10)
        print "Utilisation d'%sun point de VIDE%s, reduction des dommages (%s-10=%s)" % (JAUNE, NATIVE, damage, new_damage)
        return new_damage, void_left-1
    return damage, void_left

def gen_posture(is_first_to_fight, malus_point, skill_defense, air, vide):
    """ Fonction de génération de posture """
    random_number = randint(0, 3)
    postures_1_ok = ['ASSAUT', 'ASSAUT', 'ATTAQUE', 'ATTAQUE']
    postures_2_ok = ['ESQUIVE', 'ESQUIVE', 'ATTAQUE', 'ATTAQUE']
    postures_mal = ['ASSAUT', 'ASSAUT', 'ASSAUT', 'ATTAQUE']
    bonus_atk_dl = 0
    bonus_atk_dg = 0
    bonus_tn = 0
    posture = None
    if malus_point >= 5:
        posture = postures_mal[random_number]
    else:
        if is_first_to_fight:
            posture = postures_1_ok[random_number]
        else:
            posture = postures_2_ok[random_number]
    if posture is "ASSAUT":
        bonus_atk_dl = 2
        bonus_atk_dg = 1
        bonus_tn = -10
    elif posture is "ESQUIVE":
        bonus_tn = int(launch_dices(skill_defense + air, air, vide)/2)
    return posture, bonus_atk_dl, bonus_atk_dg, bonus_tn

def joueur_attaque(armure, point_vie, terre, reduction):
    """ Attaque du joueur """
    print "Attaquez. ND=%s, PV=%s (MALUS=%s, REDUC=%s)" % (armure, point_vie, malus(point_vie, terre), reduction)
    dmg = raw_input("Si vous touchez, écrivez les dégâts subits (sinon faites Entrée) : ")
    if dmg is "":
        print "%sVous ne touchez pas l'adversaire%s" % (ROUGE, NATIVE)
        print ""
        return point_vie
    point_vie -= max(0, int(dmg) - reduction)
    print "L'adversaire subit %s%s%s dégâts !" % (VERT, max(0, int(dmg) - reduction), NATIVE)
    print ""
    detect_death(point_vie, terre)
    return point_vie

def joueur_attaque_new(nom, armure, point_vie, terre, reduction, vide_left, bonus_dmg=0, bonus_atk=0):
    """ Attaque du joueur """
    print "%s Attaquez. ND=%s, PV=%s (MALUS=%s, REDUC=%s)" % (nom, armure, point_vie, malus(point_vie, terre), reduction)
    # dmg = raw_input("Si vous touchez, écrivez les dégâts subits (sinon faites Entrée) : ")
    atk = launch_dices()
    if dmg is "":
        print "%sVous ne touchez pas l'adversaire%s" % (ROUGE, NATIVE)
        print ""
        return point_vie, vide_left
    dmg, vide_left = do_i_reduct_damage(dmg, point_vie, terre, reduction, vide_left)
    point_vie -= max(0, int(dmg) - reduction)
    print "L'adversaire subit %s%s%s dégâts !" % (VERT, max(0, int(dmg) - reduction), NATIVE)
    print ""
    detect_death(point_vie, terre)
    return point_vie, vide_left

def joueur_2e_attaque(armure, point_vie, terre, reduction):
    """ 2e attaque du joueur """
    var = raw_input("Avez-vous une deuxième attaque ? [y/N/q]")
    if var is 'y':
        point_vie = joueur_attaque(armure, point_vie, terre, reduction)
    elif var is 'q':
        sys.exit(0)
    print ""
    return point_vie

def joueur_2e_attaque_new(nom, armure, point_vie, terre, reduction, vide_left):
    """ 2e attaque du joueur """
    var = raw_input("Avez-vous une deuxième attaque ? [y/N/q]")
    if var is 'y':
        return joueur_attaque_new(nom, armure, point_vie, terre, reduction, vide_left)
    elif var is 'q':
        sys.exit(0)
    print ""
    return point_vie, vide_left

def adversaire_attaque(atk_des_lances, atk_des_gardes, dmg_des_lances, dmg_des_gardes, vide, point_vie, terre, bonus=0, bonus_atk=0):
    """ Attaque de l'adversaire """
    print "Adversaire vous attaque et fait %s%s%s" % (ROUGE, max(0, (launch_dices(atk_des_lances, atk_des_gardes, vide) - malus(point_vie, terre)) + bonus_atk), NATIVE)
    var = raw_input("Est-ce qu'il touche ? [Y/n/q]")
    if var is 'n':
        print "%sAdversaire rate son attaque%s" % (VERT, NATIVE)
    elif var is 'q':
        sys.exit(0)
    else:
        print "Les dommages sont de %s%s%s" % (ROUGE, int(launch_dices(dmg_des_lances, dmg_des_gardes, vide) + bonus), NATIVE)
    print ""

def duel(modifier):
    """ Askira TSURUSHI, rang 3
    Utilisation du vide
    """
    nom_1 = 'Akira Tsurushi'
    terre_1 = 2
    air_1 = 3
    vide_1 = 3
    vide_restant_1 = vide_1
    armor_class_1 = 5+air_1*5+5+10 # Armure légère + Lion
    point_vie_1 = 5*terre_1+7*terre_1*2
    reduction_1 = 3 # Armure légère
    distance = modifier*5

    nom_2 = 'Samui Hida'
    terre_2 = 3
    air_2 = 3
    eau_2 = 3
    vide_2 = 3
    feu_2 = 3
    rank_2 = 3
    vide_restant_2 = 0
    armor_class_2 = 5+air_2*5+10 # Armure lourde
    point_vie_2 = 5*terre_2+7*terre_2*2
    reduction_2 = 8 # Armure légère + naturel
    skill_defense_2 = 2
    skill_kenjutsu_2 = 4 # En réalité arme lourde

    print "%s vs %s" % (nom_1, nom_2)
    # Premier tour
    print "%s %scommence en premier.%s" % (nom_1, ROUGE, NATIVE)
    print ""
    # CHOIX de la POSTURE
    posture_1, bonus_tn_1 = ['ATTAQUE', 0]
    if distance > 0:
        print "%s est à %sm de vous. Vous ne pouvez avancer que de 3m en DEFENSE, 5m en ATTAQUE et 10m ASSAUT." % (nom_1, distance)

    if distance > 0:
        posture_2 = "DEFENSE"
        bonus_atk_dl_2 = 0
        bonus_atk_dg_2 = 0
        bonus_tn_2 = 5
    else:
        posture_2, bonus_atk_dl_2, bonus_atk_dg_2, bonus_tn_2 = gen_posture(False, malus(point_vie_2, terre_2), skill_defense_2, air_2, vide_2)

    print "La posture de %s est %s%s%s. Celle de %s est %s%s%s." % (nom_1, JAUNE, posture_1, NATIVE, nom_2, JAUNE, posture_2, NATIVE)


    # ATTAQUE ADVERSAIRE 1
    if distance > 0:
        point_vie, vide_restant = joueur_attaque_new(nom_1, armor_class_1 + bonus_tn_1, point_vie_1, terre_1, reduction_1, vide_restant_1)
    else:
        point_vie, vide_restant = joueur_attaque_new(nom_1, armor_class_1 + bonus_tn_1, point_vie_1, terre_1, reduction_1, vide_restant_1, bonus_atk=-10)

    if distance > 0:
        if posture_2 is "ASSAUT":
            distance -=10
        avance = raw_input("De combien de mètres avancez-vous ? ")
        if avance is "":
            print "%sVous n'avancez pas.%s" % (ROUGE, NATIVE)
            avance = 0
        distance -= int(avance)
        print ""
    if distance <= 0:
        # ATTAQUE JOUEUR 2
        point_vie_2, vide_restant_2 = joueur_attaque_new(nom_2, armor_class_2 + bonus_tn_2, point_vie, terre_2, reduction_2, vide_restant_2)
        # 2e ATTAQUE JOUEUR 2
        point_vie, vide_restant = joueur_2e_attaque_new(armor_class + bonus_tn, point_vie, terre, reduction, vide_restant)


    # En boucle
    while point_vie > 0:
        # CHOIX de la POSTURE ADVERSAIRE
        posture, bonus_tn = ['ATTAQUE', 0]
        # ATTAQUE ADVERSAIRE
        print "La posture de l'adversaire est %s%s%s." % (JAUNE, posture, NATIVE)
        if distance > 0:
            adversaire_attaque(7, 3, 8, 2, vide, point_vie, terre)
        else:
            adversaire_attaque(7, 3, 8, 2, vide, point_vie, terre, bonus_atk=-10)

        # CHOIX de la POSTURE JOUEUR
        if distance > 0:
            print "L'adversaire est à %sm de vous. Vous ne pouvez avancer que de 3m en DEFENSE, 5m en ATTAQUE et 10m ASSAUT." % distance
        raw_input("Choisissez votre posture.")
        if distance > 0:
            avance = raw_input("De combien de mètres avancez-vous ? ")
            if avance is "":
                print "%sVous n'avancez pas.%s" % (ROUGE, NATIVE)
                avance = 0
            distance -= int(avance)
            print ""
        if distance <= 0:
            # ATTAQUE JOUEUR
            point_vie, vide_restant = joueur_attaque_new(armor_class + bonus_tn, point_vie, terre, reduction, vide_restant)
            # 2e ATTAQUE JOUEUR
            point_vie, vide_restant = joueur_2e_attaque_new(armor_class + bonus_tn, point_vie, terre, reduction, vide_restant)

duel(3)
