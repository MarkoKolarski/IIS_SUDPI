DELETE FROM KORISNIK;
DELETE FROM LOGISTICKI_KOORDINATOR;
DELETE FROM SKLADISNI_OPERATER;
DELETE FROM NABAVNI_MENADZER;
DELETE FROM FINANSIJSKI_ANALITICAR;
DELETE FROM KONTROLOR_KVALITETA;
DELETE FROM ADMINISTRATOR;

-- USERS -- password for all users is 'asdf1234'
-- user: admin@gmail.com
-- user: fa@gmail.com
-- user: nm@gmail.com
-- user: kk@gmail.com
-- user: so@gmail.com
-- user: lk@gmail.com

Insert into KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K) values ('pbkdf2_sha256$870000$B3xR7ru7zpmuld5qdzIpqC$BsV3vuNoa+jF9zeJI6dAsFGyCvb9gfo7wKVZ1NtU06s=',null,0,'admin@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 06.47.28.960782000 PM','DD-MON-RR HH.MI.SSXFF AM'),1,'admin','admin','admin@gmail.com','administrator');
Insert into KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K) values ('pbkdf2_sha256$870000$Fs66hQbo0aNq4RRk0jDr7G$/IqDyqwzz5xvl4UKKw6i017cAdSN2xYzRPysZ/eqsIQ=',null,0,'fa@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 06.47.54.013286000 PM','DD-MON-RR HH.MI.SSXFF AM'),2,'fa','fa','fa@gmail.com','finansijski_analiticar');
Insert into KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K) values ('pbkdf2_sha256$870000$fAO2m0Cz8Tq8mcHM4aDvjZ$X9CbeztmdKPRYrv5o0iJxAIagaWq7vuXq4Mp1WkaxpQ=',null,0,'nm@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 06.48.06.375977000 PM','DD-MON-RR HH.MI.SSXFF AM'),3,'nm','nm','nm@gmail.com','nabavni_menadzer');
Insert into KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K) values ('pbkdf2_sha256$870000$Ak4c4lNfzUPEvtURtnpRcY$HObZg0hIVJBfVu5Kr2SRNLWIvtGFRstAAOhFkeCTzNE=',null,0,'kk@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 06.48.24.992730000 PM','DD-MON-RR HH.MI.SSXFF AM'),4,'kk','kk','kk@gmail.com','kontrolor_kvaliteta');
Insert into KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K) values ('pbkdf2_sha256$870000$8qdZ57YzsnWq5GEGYMacwq$cNPKV4mHgyhJSsnaE3xPNiNGtW49y9j3wqOwK83MSUQ=',null,0,'so@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 06.48.58.099532000 PM','DD-MON-RR HH.MI.SSXFF AM'),5,'so','so','so@gmail.com','skladisni_operater');
Insert into KORISNIK (PASSWORD,LAST_LOGIN,IS_SUPERUSER,USERNAME,FIRST_NAME,LAST_NAME,EMAIL,IS_STAFF,IS_ACTIVE,DATE_JOINED,SIFRA_K,IME_K,PRZ_K,MAIL_K,TIP_K) values ('pbkdf2_sha256$870000$73qKNuQE9hQk4bwxlStUmZ$SpJxoVY0PAaE64kKYsa344M/uZh2zWT1Myb4t+3EqN8=',null,0,'lk@gmail.com',null,null,null,0,1,to_timestamp('08-OCT-25 06.49.12.522763000 PM','DD-MON-RR HH.MI.SSXFF AM'),6,'lk','lk','lk@gmail.com','logisticki_koordinator');
Insert into NABAVNI_MENADZER (ID,KORISNIK_ID) values (1,3);
Insert into SKLADISNI_OPERATER (ID,KORISNIK_ID) values (1,5);
Insert into ADMINISTRATOR (ID,KORISNIK_ID) values (1,1);
Insert into KONTROLOR_KVALITETA (ID,KORISNIK_ID) values (1,4);
Insert into LOGISTICKI_KOORDINATOR (ID,KORISNIK_ID) values (1,6);
Insert into FINANSIJSKI_ANALITICAR (ID,KORISNIK_ID) values (1,2);
COMMIT;