
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from scipy.stats import uniform
from scipy.stats import norm
from scipy.stats import binom
import scipy.stats as sp
from scipy.stats import t
import scipy.stats as stats
from scipy import stats

import math
from collections import Counter
from scipy.integrate import quad
from scipy.stats import uniform, norm, binom, poisson, expon, gamma, t, chi2, f, beta
from scipy.stats import bernoulli
from scipy.stats import ttest_rel

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import json 

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()


############################################################


# 1. 날씨 요인 ############################################################

rain = pd.read_csv('./rain.csv')
rain.info()
rain.head()

