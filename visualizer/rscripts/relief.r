#RReliefF IMPORTANCE
#OpenTuner visualizer v1.0
library(FSelector)

args <- commandArgs(TRUE)
df <- read.csv(args[1])
df <- df[is.finite(df$time),]

weights <- relief(time~., data = data, neighbours.count = 20, sample.size = 200)

write.csv(weights, file=args[2])

#updating the database
con <- dbConnect(RSQLite::SQLite(), dbname=args[3])
concat <- function(..., sep='') {
    paste(..., sep=sep, collapse=sep)
}
query <- concat("UPDATE visualizer_analysis SET result_doc=","'",args[2],"', ","status='completed' where visualizer_analysis.id=",args[4])
q <- dbSendQuery(conn = con, query)
dbDisconnect(con)

