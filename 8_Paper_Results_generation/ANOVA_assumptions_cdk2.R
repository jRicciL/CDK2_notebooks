library(rstatix)
library(ggpubr)
library(tidyr)
library(dplyr)

df = read.csv('Documents/Doctorado/Proteinas_modelo/ML-Ensemble-Docking/CDK2/ANALISIS/8_Paper_Results_generation/cv30x4_cdk2.csv', header = TRUE)

df = df %>%
  filter(X == 'roc_auc') %>%
  select(-X.1, -X)

# Melting the data
df_melt <- df  %>%
  mutate(rep = factor(1:nrow(.))) %>%
  pivot_longer(cols=c(everything(), -rep), 
               names_to='method', 
               values_to='score')

# Check for outliers
df_melt %>%
  group_by(method) %>%
  identify_outliers(score)

df_melt %>%
  group_by(method) %>%
  shapiro_test(score)

shapiro.test(df$csMIN)

anova <- aov(score ~ method + rep, data=df_melt)
print(summary(anova))


res.aov <- anova_test(data = df_melt, dv = score, 
                      wid = rep, within = method)
get_anova_table(res.aov)
res.aov
