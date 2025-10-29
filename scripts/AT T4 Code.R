# Load tidyverse
pacman::p_load(tidyverse)
pacman::p_load(moments)

# Loading merged and cleaned datasets
merged <- read.csv("merged_no_vle.csv")
vle <- read.csv("vle_merged.csv")
all_data <- read.csv("all_data.csv")

summary(all_data)
# Removing missing date_registration row in all_data
# Removing missing date rows in all_data
all_data <-
  all_data %>% 
  filter(date_registration != is.na(date_registration),
         date != is.na(date))
summary(all_data$date_registration); summary(all_data$date)

# Changing date_unregistration so that every row with a numeric entry is changed to "In-Active"
all_data <-
  all_data %>% 
  mutate(date_unregistration = ifelse(date_unregistration != "Active", "In-Active", date_unregistration))

# Changing id variables and is_banked from numeric to character
all_data <-
  all_data %>% 
  mutate(id_assessment = as.character(id_assessment),
         id_student = as.character(id_student),
         id_site = as.character(id_site),
         is_banked = as.character(is_banked))

# Changing num_of_prev_attempts and module_presentation_length to factor variables
all_data <-
  all_data %>% 
  mutate(num_of_prev_attempts = as.factor(num_of_prev_attempts),
         module_presentation_length = as.factor(module_presentation_length))


# Univariate analysis on all_data
univariate <- function (x) {
  if (is.numeric(x)) {
    x_avg <- mean(x)
    x_med <- median(x)
    x_range <- range(x)
    x_var <- var(x)
    x_skew <- skewness(x)
    x_kurt <- kurtosis(x)
    sum <- summary(x)
    x_quart_1 <- sum[2]
    x_quart_3 <- sum[5]
    return(list("mean" = x_avg,
                "median" = x_med,
                "range" = x_range,
                "variance" = x_var,
                "skewness" = x_skew,
                "kurtosis" = x_kurt,
                "First Quartile" = x_quart_1,
                "Third Quartile" = x_quart_3)) 
  }
  if (is.character(x) | is.factor(x)) {
    x_freq <- table(x)
    x_unique <- unique(x)
    if (length(x_unique) > 25) {
      return("id variable")
    }
    return("frequency" = x_freq)
  }
}

# Function to apply univariate analysis on a data frame
univariate_data_frame <- function(data_frame) {
  column_summary <- lapply(data_frame, univariate)
  return(column_summary)
}

univariate_data_frame(all_data)

# hist_bar function creates histograms for numerical data and bar charts for categorical data
hist_bar <- function(x, x_name, bins = 15) {
  if (is.numeric(x)) {
    gg_x <- 
      ggplot(data = data.frame(x),
             mapping = aes(x = x)) +
      geom_histogram(fill = "lightblue",
                   color = "black",
                   bins = bins) +
      theme_bw() +
      labs(x = x_name,
           y = "Count",
           title = paste("Histogram of", x_name))  
    return(gg_x)
  }
  if (is.character(x) | is.factor(x)) {
    if (length(unique(x)) > 25) {return ("id variable")} else {
      gg_x <- 
        ggplot(data = data.frame(x),
               mapping = aes(x = x)) +
        geom_bar(fill = "dodgerblue3",
                 color = "black") +
        theme_bw() +
        labs(x = x_name,
             y = "Count",
             title = paste("Bar Chart of", x_name))
      return(gg_x)
    }
  }
}

hist_bar_data_frame <- function(data_frame) {
  graphs <- mapply(hist_bar,
                       x = data_frame,
                       x_name = names(data_frame),
                       SIMPLIFY = F)
  return(graphs)
}
hist_bar_data_frame(all_data)

# box function creates boxplots for numerical data
box <- function(y, y_name) {
  if(is.numeric(y)) {
    gg_y <- 
      ggplot(data = data.frame(y),
             mapping = aes(y = y)) +
      geom_boxplot(fill = "#00945C",
                     color = "black") +
      theme_bw() +
      labs(y = y_name,
           title = paste("Boxplot of", y_name))  
    return(gg_y)
  } else {return("not numeric")}
}

box_data_frame <- function(data_frame) {
  graphs <- mapply(box,
                   y = data_frame,
                   y_name = names(data_frame),
                   SIMPLIFY = F)
  return(graphs)
}
box_data_frame(all_data)

# Creating scatterplots for bivariate analysis
scatter <- function(x, x_name, y, y_name, color) {
  gg_scatter <- 
    ggplot(data = data.frame(x),
           mapping = aes(x = x,
                         y = y)) +
    geom_point(color = color) +
    theme_bw() +
    labs(x = x_name,
         y = y_name)  
  return(gg_scatter)
}

scatter(all_data$studied_credits, "Studied Credits", all_data$score, "Score", "purple")
scatter(all_data$score, "Score", all_data$sum_click, "Clicks", "darkgreen")

# Creating bivariate boxplot
ggplot(data = all_data,
       mapping = aes(y = score,
                     x = code_module)) +
  geom_boxplot(fill = "violetred2") +
  theme_bw() +
  labs(x = "Module",
       y = "Score",
       title = "Score by Module")
  
# Multvariate analysis
ggplot(data = all_data,
       mapping = aes(x = score,
                     y = sum_click)) +
  geom_point(color = "cornflowerblue") +
  theme_bw() +
  labs(title = "Clicks vs Score by Final Result",
       x = "Score",
       y = "Clicks") +
  facet_wrap(~final_result,
             nrow = 4,
             scales = "free")
