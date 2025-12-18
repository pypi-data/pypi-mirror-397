# -*- coding: utf-8 -*-
import numpy as np
from math import pi, sin, cos, degrees, acos
from logging import getLogger


def cellshape(cellmat):
    """
    From cell matrix to a, b, c, alpha, beta, and gamma.
    """
    a = np.linalg.norm(cellmat[0])
    b = np.linalg.norm(cellmat[1])
    c = np.linalg.norm(cellmat[2])
    alpha = degrees(acos((cellmat[1] @ cellmat[2]) / (b * c)))
    beta = degrees(acos((cellmat[2] @ cellmat[0]) / (c * a)))
    gamma = degrees(acos((cellmat[0] @ cellmat[1]) / (a * b)))
    return a, b, c, alpha, beta, gamma


def cellvectors(a, b, c, A=90, B=90, C=90):
    """
    Generate cell vectors from a,b,c and alpha, beta, gamma.
    """
    # probably same as six2nine in rigid.py
    logger = getLogger()
    A *= pi / 180
    B *= pi / 180
    C *= pi / 180
    sA, cA = sin(A), cos(A)
    sB, cB = sin(B), cos(B)
    sC, cC = sin(C), cos(C)
    ea = np.array([1.0, 0.0, 0.0])
    eb = np.array([cC, sC, 0])
    # ec.ea = ecx = cos(B)
    # ec.eb = ecx*ebx + ecy*eby = cos(A)
    ecx = cB
    ecy = (cA - ecx * eb[0]) / eb[1]
    ecz = (1 - ecx**2 - ecy**2) ** 0.5
    ec = np.array([ecx, ecy, ecz])
    return np.vstack([ea * a, eb * b, ec * c])
