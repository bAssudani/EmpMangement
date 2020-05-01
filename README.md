A python project which provides a good employee management system.
It uses flask and MySql 
It has 3 logins - i)Admin
                - ii)Manager
                -iii)Employee
Employee Dashboard -Employee could see there progress,leaves -applied or approved , manager remarks , their projects etc 
Manager Dashboard - Manager can see his/her subordinates , their progress , projects leaves and has option to approve or reject
Admin Dashboard -Admin has access to add , remove employees or to edit their details .
                 Admin can see the profiles of all employees and graphs based on the projects the are in or there salary distribution
                 Admin can update profile pictures of other employees.
A chatbot functionality is provided which answers queries of other employees.
These data is stored in redis and the application is docker containerized
