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

        # Verarbeite die Belohnung (Reward), falls eine ausgewählt wurde
        if len(input_sequence) > 3:
            self.middleman.motor_input(f"KEY PRESSED: R", agent)
            self.middleman.motor_input(input_sequence[3], agent)
        else:
            print("Niemand wurde für die Belohnung ausgewählt.")

        # Verarbeite die Bestrafung (Punish), falls eine ausgewählt wurde
        if len(input_sequence) > 5:
            self.middleman.motor_input(f"KEY PRESSED: P", agent)
            self.middleman.motor_input(input_sequence[5], agent)
        else:
            print("Niemand wurde für die Bestrafung ausgewählt.")
