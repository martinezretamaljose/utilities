# qoxdlot - a multple entry boxplot formula for R
#   it's like boxplot, but b and p were rotated 180 degrees
# The key behind this script is to produce a multiple entry boxplot without
# requiring the ggplot graphic style (which I don't like, by the way).
# some extra libraries are used on this example, but my goal is to not use any
# of them when the function is called.

library(zoo)
library(RColorBrewer)
library(rstudioapi)
library(stringr)

# routing for this script's current directory and turning into the wd
main <- dirname(getActiveDocumentContext()$path); setwd(main)

# Calling the input data
input_data <- read.table(file.path('t2m_series_2024.txt'),
                         header = TRUE, sep = ";")
# this file is composed by daily mean temperatures of 4 stations in 2024.
# it has three columns:
# 1) date, in dd-mm-yyyy format
# 2) station name
# 3) daily mean temperature, in Celsius degrees.

# there might be empty or non-numerical values in the value column,
# so this one must be coerced to numeric, NA values will be deprecated later.
input_data$Valor_t2m <- as.numeric(input_data$Valor_t2m)

# deprecating NA values
input_data <- na.omit(input_data)

# before plotting anything, it is important to understand what it is needed  
# to plot. In this example, we want to show variations in daily mean temperature
# by month and by station; so my first order will be the month, and the second 
# order will be the station names.

# before converting orders, the date column must be converted to YYYY-MM-DD
# format.
input_data$date <- as.Date(paste(substr(input_data$Fecha,7,10),
                                 substr(input_data$Fecha,4,5),
                                 substr(input_data$Fecha,1,2),
                                 sep="-"))
input_data$month <- format(input_data$date,"%b")

# setting orders for boxplot
first_order <- unique(input_data$month)
second_order <- unique(input_data$Estacion)

# and here comes the function
qoxdlot <- function(data_col,order_1,order_2,cat_1,cat_2,colors,ylab,main){
  #' @title Multiple entry boxplot under R's graphic style.
  #' @param data_col dataframe, single column of numerical values
  #' @param order_1 dataframe, single column of factors, characters or strings
  #' @param order_2 dataframe, single column of factors, characters or strings
  #' @param cat_1 single column, character or factor
  #' @param cat_2 single column, character or factor
  #' @param colors list of colors, must be same length of cat_2
  #' @param ylab string, text to display on boxplot's y-axis.
  #' @param main string, text to display as plot title
  #' @return a boxplot.
   
  input <- data.frame(x=data_col, 
                      order_1 = order_1,
                      order_2 = order_2,
                      box=NA)
  for (i in 1:length(first_order)){
    for (j in 1:length(second_order)){
      z <- j + (i-1)*length(cat_2)
      loc <- which(input$order_1==cat_1[i] & input$order_2==cat_2[j])
      input$box[loc] <- z
    }
  }
  # if there are empty values, they will be deprecated.
  input <- na.omit(input)
  vertical_ticks <- seq(min(input$box)-0.5,
                        max(input$box)+0.5,
                        length(cat_2))
  axis_ticks <- seq(min(input$box)+(length(cat_2)-1)/2,
                    max(input$box)-(length(cat_2)-1)/2,
                    length(cat_2))
  boxplot(input$x~input$box,col=colors,xlab=NA,ylab=ylab,xaxt='n',
          main=main)
  abline(v=vertical_ticks,lty=2,col='#666666')
  axis(side=1, at = axis_ticks, labels=cat_1)
}

# test No.1
png(file.path('test_1.png'),width=1600,height=900, pointsize = 20)
qoxdlot(data_col = input_data$Valor_t2m,
        order_1 = input_data$month,
        order_2 = input_data$Estacion,
        cat_1 = first_order,
        cat_2 = second_order,
        colors = brewer.pal(n=length(second_order),name="Set1"),
        ylab = "[°C]",main = "Daily mean temperatures, by month and station"
        )
# additions
legend('bottomleft',
       fill=brewer.pal(n=length(second_order),name="Set1"),
       legend=second_order)
box(lwd=2)
dev.off()

# test No.2 - What if there is changes on the orders?
first_order_a <- first_order[c(4,5,6,7,8,9,10,11,12,1,2,3)]
second_order_a <- second_order[c(3,4,2,1)]

png(file.path('test_2.png'),width=1600,height=900, pointsize = 20)
qoxdlot(data_col = input_data$Valor_t2m,
        order_1 = input_data$month,
        order_2 = input_data$Estacion,
        cat_1 = first_order_a,
        cat_2 = second_order_a,
        colors = brewer.pal(n=length(second_order),name="Set1"),
        ylab = "[°C]",main = "Daily mean temperatures, test No.2"
)
# additions
legend('bottomright',
       fill=brewer.pal(n=length(second_order),name="Set1"),
       legend=second_order_a)
box(lwd=2)
dev.off()