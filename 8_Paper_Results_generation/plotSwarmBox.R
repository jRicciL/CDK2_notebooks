library(extrafont)
library(ggthemes)
library(plyr)
library(tidyr)
library(dplyr)
library('gghalves')
# library('DescTools')
library("scales")
library(matrixStats)
library(tidyverse)

# lb <- function(x) { MedianCI(x, 0.95)['lwr.ci'] }
lb <- function(x) { median(x) - 1.57*IQR(x)/sqrt(length(x)) }
# ub <- function(x) { MedianCI(x, 0.95)['upr.ci'] }
ub <- function(x) { median(x) + 1.57*IQR(x)/sqrt(length(x)) }

plot_swarm_box <- function(df, cbbPalette, decreasing_order = TRUE, y_label='AUC-ROC', 
                           y_min=0.4, y_max=1, dot_size=8, bin_width=0.001, base_h_line=0.5) {
    
    names_order <- names(sort(apply(df, 2, FUN=median), decreasing = decreasing_order))
    df <- df[, names_order]
    
    df_melted <- df %>%
        mutate(rep = factor(1:nrow(.))) %>%
        pivot_longer(cols=c(everything(), -rep), names_to='method', values_to='score')
    
    df_melted$method <- factor(df_melted$method, levels = names_order)
   

    sumld<- ddply(df_melted, ~method, summarise, 
                  mean = mean(score), 
                  median = median(score), 
                  lower = lb(score), 
                  upper = ub(score))

    ggplot(data = df_melted, 
           mapping = aes(x = method, 
                         y = score, 
                         fill = method)) + 
      geom_hline(yintercept= base_h_line, linetype="dashed", color="#444444") +
      # geom_half_violin(scale = "area", trim = TRUE, side='r', width=0.8, lwd=0.2,
      #                  alpha=0.25, position = position_nudge(x = 0.1)) +
      # geom_boxplot(notch=TRUE, width=0.5, lwd=0.2, color='black',
      #             outlier.size=0.2,
      #             position = position_nudge(x = -0.17)) +
      geom_violin(width=01, lwd=0.2, color='black') +
      theme(text=element_text(family="Trebuchet MS")) + 
      stat_summary(fun.data = mean_sdl, 
                   fun.args = list(mult = 1), 
                   geom = "pointrange", 
                   position = position_nudge(0.5)) +
      geom_errorbar(data = sumld, aes(ymin = lower, ymax = upper, y = median), 
                    position = position_nudge(x = -0.17), width = 0) + 
      geom_point(data = sumld, aes(x = method, y = median), colour='#000000',
                    position = position_nudge(x = -0.17), size = 0.8, stroke=0.5) +
      geom_point(data = sumld, aes(x = method, y = median), colour='white',
                    position = position_nudge(x = -0.17), size = 0.7, stroke=0.1) +
      # geom_dotplot(binaxis = "y", 
      #              dotsize = dot_size, 
      #              stackdir = "up", 
      #              binwidth = bin_width, 
      #              alpha = 0.9,
      #              stroke=0,
      #              position = position_nudge(0.08)) +
        theme(legend.position = "none", panel.border = element_rect(colour = "black", fill=NA, size=1),
              panel.background = element_rect(fill = "white",
                                    colour = "white",
                                    size = 0.5, linetype = "solid"),
              panel.grid.major.y = element_line(size = 0.1, linetype = 'solid', colour = "grey"), 
              panel.grid.minor.y = element_line(size = 0.05, linetype = 'solid', colour = "darkgrey"),
              panel.grid.major.x = element_blank()
             ) + 
          labs(x = "Methods (ML/CS)", 
               y = y_label) +
      scale_y_continuous(breaks = seq(y_min, y_max, 0.1), limits = c(y_min, y_max)) +  
    #   scale_fill_brewer(palette = "") +
      scale_fill_manual(values=cbbPalette)
}

plot_violin<- function(df, cbbPalette, decreasing_order = TRUE, y_label='AUC-ROC', 
                           y_min=0.4, y_max=1, dot_size=8, bin_width=0.001, base_h_line=0.5) {
    
    names_order <- names(sort(apply(df, 2, FUN=median), decreasing = decreasing_order))
    df <- df[, names_order]
    
    df_melted <- df %>%
        mutate(rep = factor(1:nrow(.))) %>%
        pivot_longer(cols=c(everything(), -rep), names_to='method', values_to='score')
    
    df_melted$method <- factor(df_melted$method, levels = names_order)
   

    sumld<- ddply(df_melted, ~method, summarise, 
                  mean = mean(score), 
                  median = median(score), 
                  lower = lb(score), 
                  upper = ub(score))

    ggplot(data = df_melted, 
           mapping = aes(x = method, 
                         y = score, 
                         fill = method)) + 
      geom_hline(yintercept= base_h_line, linetype="dashed", color="#444444", lwd=0.3) +
      geom_violin(width=1.2, lwd=0.3, color='black', alpha=0.6, trim=FALSE) +
      geom_boxplot(notch=TRUE, width=0.2, lwd=0.2, color='black',
                  outlier.size=0.1) +
      theme(text=element_text(family="Trebuchet MS")) + 
      stat_summary(fun.data = mean_sdl, 
                   fun.args = list(mult = 1), 
                   geom = "pointrange", 
                   position = position_nudge(0.5)) +
      geom_errorbar(data = sumld, aes(ymin = lower, ymax = upper, y = median), 
                    width = 0) + 
      geom_point(data = sumld, aes(x = method, y = median), colour='#000000',
                    size = 0.6, stroke=0.5) +
      geom_point(data = sumld, aes(x = method, y = median), colour='white',
                    size = 0.6, stroke=0.1) +
      # geom_dotplot(binaxis = "y", 
      #              dotsize = dot_size, 
      #              stackdir = "up", 
      #              binwidth = bin_width, 
      #              alpha = 0.9,
      #              stroke=0,
      #              position = position_nudge(0.08)) +
        theme(legend.position = "none", panel.border = element_rect(colour = "black", fill=NA, size=1),
              panel.background = element_rect(fill = "white",
                                    colour = "white",
                                    size = 0.5, linetype = "solid"),
              panel.grid.major.y = element_line(size = 0.1, linetype = 'solid', colour = "grey"), 
              # panel.grid.minor.y = element_line(size = 0.05, linetype = 'solid', colour = "darkgrey"),
              # axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1),
              panel.grid.major.x = element_blank()
             ) + 
          labs(x = "Methods (ML/CS)", 
               y = y_label) +
      scale_y_continuous(breaks = seq(y_min, y_max, 0.1), limits = c(y_min, y_max)) + 
      scale_x_discrete(guide = guide_axis(n.dodge = 2)) + 
    #   scale_fill_brewer(palette = "") +
      scale_fill_manual(values=cbbPalette)
}


add_ref_values <- function(text, value, color='#888888', y_add=0.02, x=1, size=2.3) {
        list(
            geom_hline(yintercept= value, linetype="dotted", color=color, size=0.3),
            geom_text(aes(x=x, y= value + y_add), label=text, color=color,  size=size)
        )
    }


library(tidyverse)
library(extrafont)
library(ggthemes)
library(plyr)


plot_lines <- function(df, cbbPalette, y_label='AUC-ROC', y_min=0.4, y_max=1, switch_x=TRUE, 
                       line_size=1, point_size=2.2, error_dodge=0.05, error_width=1.5, error_size=1,
                       base_h_line=0.5, x_label="Percentage of shuffled labels (%)", title='') {

    ggplot(data = df, 
           mapping = aes(x = index, 
                         y = mean, 
                         color = method)) + 
        geom_hline(yintercept= base_h_line, 
                   linetype="dashed", color="#333333") +
        geom_line(size=line_size) + 
        theme(text=element_text(family="Trebuchet MS")) + 
        {if(switch_x)scale_x_reverse()} +
        geom_errorbar(aes(ymin=mean-std, ymax=mean+std), width=error_width, size=error_size, position=position_dodge(error_dodge)) +
        geom_errorbar(aes(ymin=mean-std, ymax=mean+std), width=error_width, size=error_size, position=position_dodge(error_dodge)) +
        geom_point(color='black', size=point_size + 1, stroke=0.5)+
        geom_point(size=point_size, stroke=0.5)+
        ggtitle(title) +
        scale_y_continuous(breaks = seq(y_min, y_max, 0.1), limits = c(y_min, y_max)) + 
        theme(panel.border = element_rect(colour = "black", fill=NA, size=1),
             panel.background = element_rect(fill = "white",
                                        colour = "white",
                                        size = 0.5, linetype = "solid"),
                  panel.grid.major.y = element_line(size = 0.2, linetype = 'solid', colour = "grey"), 
                  panel.grid.minor.y = element_line(size = 0.05, linetype = 'solid', colour = "darkgrey"),
                  panel.grid.major.x = element_blank()
             ) + 
                  labs(x = x_label, y = y_label) +
        scale_color_manual(values=rev(cbbPalette), name='Method')
    }