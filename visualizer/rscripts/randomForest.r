#RANDOM FOREST IMPORTANCE
#OpenTuner visualizer v1.0
require(randomForest)
require(caret)
require("RSQLite")

args <- commandArgs(TRUE)
df <- read.csv(args[1])

#preprocessing
df <- df[is.finite(df$time),]
#control function
control <- trainControl(method = "oob")
mtryGrid <- expand.grid(mtry = 100)
rf <- train(time~., 
            data = df, 
            ntree=2000, 
            method = "rf", 
            trControl = control, 
            tuneGrid=mtryGrid,
            importance = TRUE, 
            verbose = TRUE)

fm <- rf$finalModel
write.csv(varImp(fm), file=args[2])

#updating the database
con <- dbConnect(RSQLite::SQLite(), dbname=args[3])
concat <- function(..., sep='') {
    paste(..., sep=sep, collapse=sep)
}
query <- concat("UPDATE visualizer_analysis SET result_doc=","'",args[2],"', ","status='completed' where visualizer_analysis.id=",args[4])
q <- dbSendQuery(conn = con, query)
dbDisconnect(con)