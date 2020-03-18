<u><b>DJANGO SUPERUSER</b></u><br>
<b>USERNAME: </b>sims<br>
<b>PASSWORD: </b>sims<br><hr>
<u><b>POSTGRES CONFIG</b></u><br>
<b>USERNAME: </b> sims<br>
<b>PASSWORD: </b>sims<br><hr>
<b>Steps to run:</b>
<ol>
	<li>Create a database in your postgres with name 'sims'.</li>
	<li>Create a postgres user with username = 'sims' and password = 'sims'.<br/>
		Grant this user all privileges to the database 'sims'.
		<br><b>Command:</b> GRANT ALL PRIVILEGES ON DATABASE sims TO sims;</li>
	<li>Make migrations.</li>
	<li>Migrate.</li>
	<li>Run server.</li>
</ol>
<hr>
<b>Some Conventions:</b><br>
<ul>
	<li>logoutStatus in the codebase would signify whether the logoutStatus of a particular user is True/False.</li>
	<li>Maintain sessions for each login/logout.</li>
	<li>For Non-Admin, pass non_admin = True in the context.</li>
	<li>For Admin, pass admin = True in the context.</li>
	<li>For Dealing-Admin, pass dealing_admin = True in the context.</li>
</ul>
<hr>