require(randomForest)
require(caret)

args <- commandArgs(TRUE)
df <- read.csv(args[1])

control <- trainControl(method = "oob")
mtryGrid <- expand.grid(mtry = 100)
rf <- train(time~., data = df, ntree=2000, method = "rf", trControl = control, tuneGrid=mtryGrid,
            importance = TRUE, verbose = TRUE)

fm <- rf$finalModel
print(rf$bestTune)
print(fm)
write.csv(varImp(fm), file=args[2])