class ManualInputController:
    def __init__(self, middleman):
        self.middleman = middleman

    def handle_input(self, input_sequence, agent):
        """
        Diese Methode erhält die Eingabesequenz und ruft die entsprechende
        Methode des Middleman auf, um die Aktionen zu verarbeiten.
        """
        # Verarbeite den Beitrag (Contribute)
        self.middleman.motor_input(f"KEY PRESSED: C", agent)
        self.middleman.motor_input(str(input_sequence[1]), agent)

        # Verarbeite die Belohnung (Reward)
        if len(input_sequence) > 3 and input_sequence[3] != "Z":  # "Z" bedeutet, dass niemand belohnt wird
            self.middleman.motor_input(f"KEY PRESSED: R", agent)
            self.middleman.motor_input(input_sequence[3], agent)

        # Verarbeite die Bestrafung (Punish)
        if len(input_sequence) > 5 and input_sequence[5] != "Z":  # "Z" bedeutet, dass niemand bestraft wird
            self.middleman.motor_input(f"KEY PRESSED: P", agent)
            self.middleman.motor_input(input_sequence[5], agent)
