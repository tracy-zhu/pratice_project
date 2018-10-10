library(reticulate)
source('R_base/constant.R')

read_quote_data <- function(instrument_id, trading_day){
  file_name = paste0(G_TICK_QUOTE_FILE_ROOT_FOLDER, trading_day, "/", instrument_id, ".csv")
  quote_data = read.table(file_name, header = TRUE, sep = ',')
  time_index = quote_data$Update_Time + quote_data$Update_Millisec
  rownames(quote_data) <- quote_data$Update_Time
  return(quote_data)
}