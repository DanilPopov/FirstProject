#Masha = {'city': 'Moscow', 'temperature': 20, 'wind': 'east'}
#Sasha = {'city': 'St.Petersburg', 'temperature': 25, 'wind': 'east'}
#Danil = {'city': 'Moscow', 'temperature': 22, 'wind': 'west'}
#all_names = {'Sasha': Sasha, 'Masha': Masha, 'Danil': Danil}
#name = input('Введите ваше имя: ')
#current_user = all_names.get(name, all_names['Danil'])
#print('Your city is '+current_user['city'] +
#	'\n'+ 'The temperature today is '+str(current_user['temperature']) +
#	'\n' + 'The wind blows from '+current_user['wind'])


names = ['Оля', 'Петя', 'Вася', 'Маша']
print(names[0] + ': ' + str(len(names[0])) +
	'\n' + names[1] + ': ' + str(len(names[1])) +
	'\n' + names[2] + ': ' + str(len(names[2])) +
	'\n' + names[3] + ': ' + str(len(names[3])))
