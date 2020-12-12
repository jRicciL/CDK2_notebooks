library(PMCMR)
library(reshape2)
library(ggplot2)

p_labels = c("p < 0.001", "p < 0.01", 'p < 0.05', 'NS')
names(p_labels) <- p_labels
p_colors = c('#1965DB', "#078EE1",  "#27E4C2", '#FB992A')
names(p_colors) <- p_labels

plot_p_vals_heatmap <- function(df_R) {
    df_melt <- df_R %>%
        mutate(rep = factor(1:30)) %>%
        pivot_longer(cols=c(everything(), -rep), names_to='Method', 
                     values_to='score')

    p_values <- posthoc.friedman.nemenyi.test(formula=score ~ Method | rep, data=df_melt)$p.value
    p_values <- p_values[rev(rownames(p_values)), ]

    m_p_values <- melt(p_values, na.rm = TRUE)
    m_p_values$cutoffs <- cut(m_p_values$value, breaks=c(-Inf, 0.001, 0.01, 0.05, Inf), right=TRUE, labels=p_labels)

    ggplot(data = m_p_values, aes(x=Var1, y=Var2, fill=cutoffs)) + 
      geom_tile(color='white', size=1) +
       scale_fill_manual(labels = p_labels, 
                         values = p_colors,
                        name='Significance') + 
       geom_text(aes(family="Trebuchet MS", Var1, Var2, label = round(value, 4)), color = "black", size = 3) +
       theme(text=element_text(family="Trebuchet MS"), 
             panel.background = element_rect(fill = "white"),
             legend.position = c(0.85, 0.8),
             axis.title.x = element_blank(),
             axis.title.y = element_blank(),
             axis.text.x = element_text(angle = 45, vjust = 1, hjust=1))
    
    }