from cRegression import LinearRegression

x = [1,2,3,4]
y = [2,4,6,8]

lr = LinearRegression(x, y)
print(lr.predict([5]))
