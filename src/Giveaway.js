class Giveaway {
    constructor() {
        this.commands = new Map();
        this.giveawayActive = false;
        this.poolActive = false;
        this.giveawayPool = [];
        this.poolPool = [];
    }

    openGiveaway() {
        if (this.giveawayActive) {
            return "Giveaway is already active!";
        }

        this.giveawayActive = true;
        return "Giveaway started!";
    }

    openPool() {
        if (this.poolActive) {
            return "Pool is already open!";
        }

        this.poolActive = true;
        return "Pool opened!";
    }

    enterGiveaway(username) {
        if (this.giveawayActive) {
            if (!this.giveawayPool.includes(username)) {
                this.giveawayPool.push(username);

                return `@${username}, you've successfully been entered into the giveaway.`;
            }

            return `@${username}, you've already entered the giveaway.`;
        }

        return "There is not an active giveaway.";
    }

    enterPool(username) {
        if (this.poolActive) {
            if (!this.poolPool.includes(username)) {
                this.poolPool.push(username);


                return `@${username}, you've successfully been entered into the pool.`;
            }

            return `@${username}, you've already entered the pool.`;
        }

        return "There is not an active pool.";
    }

    pullGiveaway() {
        var winner = this.giveawayPool[Math.floor(Math.random() * this.giveawayPool.length)];
        this.removeGiveawayEntry(winner);
        return winner;
    }

    clearGiveaway() {
        this.giveawayPool = [];
    }

    removeGiveawayEntry(username) {
        this.giveawayPool.splice(this.giveawayPool.indexOf(username), 1);
    }

    pullPool() {
        var winner = this.poolPool[Math.floor(Math.random() * this.poolPool.length)];
        this.removePoolEntry(winner);
        return winner;
    }

    clearPool() {
        this.poolPool = [];
    }

    removePoolEntry() {
        this.poolPool.splice(this.poolPool.indexOf(username), 1);
    }
}

module.exports = new Giveaway();