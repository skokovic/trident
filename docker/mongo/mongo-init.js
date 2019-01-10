db.createUser(
        {
            user: "trident",
            pwd: "trident",
            roles: [
                {
                    role: "readWrite",
                    db: "trident"
                }
            ]
        }
);
