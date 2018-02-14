airbnbNew = read.csv("airbnbNew_Data.csv")
airbnb = read.csv("airbnb_Data.csv")
airbnb_NormNoY = read.csv("airbnb_NormNoY_Data.csv")
airbnb_Norm = read.csv("airbnb_Norm_Data.csv")

#airbnbNew_scale(trouble[, -c(1)])

library(randomForest)

airbnb_Norm$price = airbnb_Norm$price * 699
rownames(airbnb_Norm) = airbnb_Norm$roomID
airbnb_Norm$roomID = NULL
airbnb_Norm$X = NULL

samp = sample(nrow(airbnb_Norm), 0.9 * nrow(airbnb_Norm))
train = airbnb_Norm[samp, ]
test = airbnb_Norm[-samp, ]

model <- randomForest(price ~ ., data = train)

pred <- predict(model, newdata = test)

print(pred[5])
print(airbnbNew[5])

MSE = mean((test$price - pred)^2)

library(leaflet)
library(dplyr)
library(maptools)


'
Now I would like to build an "average" dataset
This will have the mean for everything, except
long and lat
'
#airbnb_Norm[32,]

count(airbnb)

means = colMeans(airbnb_Norm)

mat <- matrix(nrow = 3330, ncol = length(means))
i = 1
for(mean in means){
  mat[, i] = rep(mean,3330)
  i = i + 1 
}

longLat = data.frame(mat,stringsAsFactors=FALSE)
#means = colMeans(longLat)

colNames = colnames(airbnb_Norm)
colnames(longLat) = colNames
print(longLat)

longLat$latitude = airbnb_Norm$latitude
longLat$longitude = airbnb_Norm$longitude


longLat
longLat$price = predict(model, newdata = longLat)
longLat

longLat$latitude = airbnbNew$latitude
longLat$longitude = airbnbNew$longitude
longLat

print(head(longLat$price,10))
print(head(airbnb$price,10))


# So it's not learning exactly from the original dataset...MSE is 147,000....
# How to generalize random forest...
head(longLat$price,500) - head(airbnb$price,500)
MSE = mean((head(longLat$price,500) - head(airbnb$price,500))^2)

# .125      beds is one bed
# .11     is 2 guests
# .125      is one bedroom

#data(quakes)

# Show first 20 rows from the `quakes` dataset
#leaflet(data = quakes[1:20,]) %>% addTiles() %>%
#  addMarkers(~long, ~lat, popup = ~as.character(mag), label = ~as.character(mag))


#{r, echo = FALSE, warning = FALSE}
library(RColorBrewer)

state_popup <- paste(longLat$price)

qpal_price <- colorQuantile("RdYlBu", longLat$price, n = 10)
leaflet(data=longLat) %>% 
  
  addProviderTiles("CartoDB.DarkMatter") %>% 
  addCircleMarkers(
  lng=longLat$longitude, 
  lat=longLat$latitude,
  group = "nhood",
  radius = 3, 
  stroke = FALSE, 
  opacity = 2, 
  color = ~qpal_price(longLat$price),
  popup = ~state_popup) %>%
  
  addLegend("topleft", pal = qpal_price, values = ~price,
  title = "Price of Listing",
  opacity = 0.7) %>% 
  
  setView(-73.97, 40.77, zoom = 11) 

' Not the best map. There seems to be no variation based on latitude and longitude.
I do not believe that. I will now pass this (longitude and lat and predicted price)
into a neural network with high generalization. See if we can get something with 
slow slopes.'

longLat$latitude = airbnb_Norm$latitude
longLat$longitude = airbnb_Norm$longitude

longLat_3column = longLat[,c('price','longitude','latitude')]
print(longLat_3column)
longLat_X = longLat_3column[,2:3]
feats <- names(longLat_X)

samp = sample(nrow(longLat_3column), 0.9 * nrow(longLat_3column))
train = longLat_3column[samp, ]
test = longLat_3column[-samp, ]

# Concatenate strings
f <- paste(feats,collapse=' + ')
f <- paste('price ~',f)

# Convert to formula
f <- as.formula(f)

#install.packages('neuralnet')
library(neuralnet)
nn <- neuralnet(f,train,hidden=c(5,5),linear.output=TRUE) #maybe smaller net

# Compute Predictions off Test Set
predicted.nn.values <- neuralnet::compute(nn,test[2:3])

# Check out net.result
print(head(predicted.nn.values$net.result))
h = predicted.nn.values$net.result
plot(nn)
print(h)

'Examining the neural network results, it seems to have not learned much at all
from the data points given. All of the data is $166.13 for every location.

It is possible this is because latitude and longitudeare not good predictors of 
cost. I am not willing to say that just yet. It is more likely that this quick 
NN implementation was done improperly. '

library(FNN)
longLat_train = longLat[,c('longitude','latitude')]

print(longLat_train)
#Need to add in some random noise, otherwise it will not accurately work.
# adding random noise, mean of 0, std of .01
longLat_train$longitude = longLat_train$longitude + rnorm2(length(longLat_train),0,.2)
longLat_train$latitude = longLat_train$latitude + rnorm2(length(longLat_train),0,.2)

pred_025 = FNN::knn.reg(train = longLat_train, test = longLat_train,
                        y = longLat_3column$price, k = 100)
print(pred_025)
pred_025[4][1]

KNN_longLat = longLat_3column
KNN_longLat$latitude = airbnbNew$latitude
KNN_longLat$longitude = airbnbNew$longitude
class(pred_025[4][[1]])
pred_025[4][[1]]

KNN_longLat$price = pred_025[4][[1]]
head(KNN_longLat$price,20)
head(longLat$price,20)
#pred_010 = FNN::knn.reg(train = X_boston, test = lstat_grid, y = y_boston, k = 10)


'Now we graph the KNN adjusted values'

state_popup <- paste(airbnbNew$price)

pal <- colorNumeric(
  palette = "YlGnBu",
  domain = airbnbNew$price
)

leaflet(data=airbnbNew) %>% 
  
  addProviderTiles("CartoDB.DarkMatter") %>% 
  addCircleMarkers(
    lng=airbnbNew$longitude, 
    lat=airbnbNew$latitude,
    group = "nhood",
    radius = 1.2, 
    stroke = FALSE, 
    opacity = 2,
    fillOpacity = .5,
    color = ~pal(price),
    popup = ~state_popup) %>%
  
  addLegend("bottomright", pal = pal, values = ~price,
            title = "Cost/Night ($)",
            labFormat = labelFormat(prefix = "$"),
            opacity = 1
  )
  
  setView(-73.97, 40.77, zoom = 11) 
  
  '
  Next let us only show the expensive places with markers.
  '
  #airbnbExpensive = airbnb[airbnb[, "price"]>700, ]
  airbnbExpensive = airbnb
  print(head(airbnbExpensive$price))
  state_popup2 <- paste(airbnbExpensive$price)
  
  pal2 <- colorNumeric(
    palette = "YlGnBu",
    domain = airbnbExpensive$price
  )
  
  leaflet(data=airbnbNew) %>% 
    
    addProviderTiles("CartoDB.DarkMatter") %>% 
    addCircleMarkers(
      lng=airbnbExpensive$longitude, 
      lat=airbnbExpensive$latitude,
      group = "nhood",
      radius = (airbnbExpensive$price^.7)/50, 
      stroke = FALSE, 
      opacity = 2,
      fillOpacity = (airbnbExpensive$price^.7)/100,
      color = ~pal2(airbnbExpensive$price),
      popup = ~state_popup2) %>%
    
    addLegend("bottomright", pal = pal2, 
              values = ~airbnbExpensive$price,
              title = "Cost/Night ($)",
              labFormat = labelFormat(prefix = "$"),
              opacity = 1
    )
  
  setView(-73.97, 40.77, zoom = 11) 
  
