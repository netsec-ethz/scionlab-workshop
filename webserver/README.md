The webserver requires setting some environment variables.
Run `cp example.env .env` and DON'T FORGET TO EDIT THE VALUES FOR PRODUCTION ;-)

## Running the whole thing

### Signup phase

To let the teams signup, run `./scionlab manage signup`
To disable signup, run it again.

### Generating configs

It is necessary to generate the configs before the start of the game rounds.
First, run `./scionlab manage teams` to save the teams to a file.
Then, run `./scionlab manage config` to generate the configs.

### Round preparation and round cleanup

Before each round, `./scionlab manage prepare` prepares all the necessary files 
in the `./rounds/cur-round` folder.

After each round, `./scionlab manage finish` collects the results of the 
previous run and clears the `./rounds/cur-round` directory.